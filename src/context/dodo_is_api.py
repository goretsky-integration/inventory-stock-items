import asyncio
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final, TypeAlias, TypeVar
from uuid import UUID

from pydantic import SecretStr

from connections.dodo_is_api import DodoISConnection
from logger import create_logger
from models import InventoryStockItem
from parsers.dodo_is_api import parse_inventory_stocks_response

__all__ = ('InventoryStocksFetchUnitOfWork',)

logger = create_logger('dodo_is_api')

T = TypeVar('T')

AccessTokenAndUnitUuids: TypeAlias = tuple[SecretStr, Iterable[UUID]]


def batched(iterable: Iterable[T], n: int) -> Iterable[list[T]]:
    iterator = iter(iterable)
    while True:
        batch = list(itertools.islice(iterator, n))
        if not batch:
            return
        yield batch


@dataclass(frozen=True, slots=True)
class InventoryStocksFetchResult:
    unit_uuids: list[UUID]
    stocks: list[InventoryStockItem] | None = None
    exception: Exception | None = None


@dataclass(frozen=True, slots=True)
class InventoryStocksFetchAllResult:
    stocks: list[InventoryStockItem]
    error_unit_uuids: set[UUID]


def flatten(nested: Iterable[Iterable[T]]) -> list[T]:
    return [item for sublist in nested for item in sublist]


class InventoryStocksFetchUnitOfWork:

    def __init__(self, connection: DodoISConnection):
        self.__connection = connection
        self.__tasks: set[AccessTokenAndUnitUuids] = set()

    def register_task(
            self,
            *,
            access_token: SecretStr,
            unit_uuids: Iterable[UUID],
    ) -> None:
        self.__tasks.add((access_token, tuple(unit_uuids)))

    async def _get_units_all_inventory_stocks(
            self,
            access_token: SecretStr,
            unit_uuids: Iterable[UUID],
    ) -> InventoryStocksFetchResult:
        unit_uuids = list(unit_uuids)
        max_pages: Final[int] = 100
        take: Final[int] = 1000
        skip: int = 0

        inventory_stocks: list[InventoryStockItem] = []

        try:
            for _ in range(max_pages):
                logger.debug(f'Fetching inventory stocks for {unit_uuids}')
                response = await self.__connection.get_inventory_stocks(
                    access_token=access_token,
                    unit_uuids=unit_uuids,
                    take=take,
                    skip=skip,
                )
                logger.debug(
                    f'Fetched inventory stocks for {unit_uuids}',
                    extra={
                        'status_code': response.status_code,
                        'body': response.text,
                    },
                )

                response_body = parse_inventory_stocks_response(
                    response=response,
                )

                inventory_stocks += response_body.stocks

                if response_body.is_end_of_list_reached:
                    break

                skip += take
        except Exception as error:
            return InventoryStocksFetchResult(
                unit_uuids=unit_uuids,
                exception=error,
            )
        return InventoryStocksFetchResult(
            unit_uuids=unit_uuids,
            stocks=inventory_stocks,
        )

    async def commit(self) -> InventoryStocksFetchAllResult:
        tasks: list[asyncio.Task[InventoryStocksFetchResult]] = []
        async with asyncio.TaskGroup() as task_group:
            for access_token, unit_uuids in self.__tasks:
                for unit_uuids_batch in batched(unit_uuids, n=30):
                    task = self._get_units_all_inventory_stocks(
                        access_token=access_token,
                        unit_uuids=unit_uuids_batch,
                    )
                    tasks.append(task_group.create_task(task))

        stocks: list[InventoryStockItem] = []
        error_unit_uuids: set[UUID] = set()
        for task in tasks:
            result = task.result()
            if result.exception is None:
                stocks += result.stocks
            else:
                logger.error(
                    f'Failed to fetch inventory stocks for {result.unit_uuids}',
                    exc_info=result.exception,
                )
                error_unit_uuids.update(result.unit_uuids)

        return InventoryStocksFetchAllResult(
            stocks=stocks,
            error_unit_uuids=error_unit_uuids,
        )

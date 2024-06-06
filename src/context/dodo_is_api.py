import asyncio
from collections.abc import Iterable
from typing import Final, TypeAlias, TypeVar
from uuid import UUID

import structlog.stdlib
from pydantic import SecretStr

from dodo_is import DodoISConnection
from models import InventoryStockItem
from parsers.dodo_is_api import parse_inventory_stocks_response

__all__ = ('InventoryStocksFetchUnitOfWork',)

logger = structlog.stdlib.get_logger('dodo_is_api')

T = TypeVar('T')

AccessTokenAndUnitUuids: TypeAlias = tuple[SecretStr, Iterable[UUID]]


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
    ) -> list[InventoryStockItem]:
        max_pages: Final[int] = 100
        take: Final[int] = 1000
        skip: int = 0

        inventory_stocks: list[InventoryStockItem] = []

        for _ in range(max_pages):
            response = await self.__connection.get_inventory_stocks(
                access_token=access_token,
                unit_uuids=unit_uuids,
                take=take,
                skip=skip,
            )

            response_body = parse_inventory_stocks_response(
                response=response,
            )

            inventory_stocks += response_body.stocks

            if response_body.is_end_of_list_reached:
                break

            skip += take

        return inventory_stocks

    async def commit(self) -> list[InventoryStockItem]:
        tasks = []
        for access_token, unit_uuids in self.__tasks:
            task = self._get_units_all_inventory_stocks(
                access_token=access_token,
                unit_uuids=unit_uuids,
            )
            tasks.append(task)

        responses: tuple[list[InventoryStockItem] | Exception] = (
            await asyncio.gather(*tasks, return_exceptions=True)
        )

        return flatten(
            [response for response in responses
             if not isinstance(response, Exception)]
        )

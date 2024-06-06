from collections.abc import Iterable
from uuid import UUID

import httpx
from pydantic import SecretStr
from structlog.contextvars import bound_contextvars

from new_types import DodoIsApiConnectionHttpClient

import structlog.stdlib

__all__ = ('DodoISConnection',)

logger = structlog.stdlib.get_logger('dodo_is_api')


def merge_uuids(uuids: Iterable[UUID]) -> str:
    return ','.join(str(uuid) for uuid in uuids)


class DodoISConnection:

    def __init__(self, http_client: DodoIsApiConnectionHttpClient):
        self.__http_client = http_client

    async def get_inventory_stocks(
            self,
            *,
            unit_uuids: Iterable[UUID],
            access_token: SecretStr,
            take: int = 1000,
            skip: int = 0,
    ) -> httpx.Response:
        request_query_params = {
            'units': merge_uuids(unit_uuids),
            'take': take,
            'skip': skip,
        }
        url = '/accounting/inventory-stocks'
        headers = {
            'Authorization': f'Bearer {access_token.get_secret_value()}',
        }
        with bound_contextvars(params=request_query_params):
            response = await self.__http_client.get(
                url=url,
                params=request_query_params,
                headers=headers,
            )
            logger.debug(
                'Retrieved inventory stocks from Dodo IS API',
                status_code=response.status_code,
            )

        return response

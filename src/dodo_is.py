from collections.abc import Iterable
from uuid import UUID

import httpx
from pydantic import SecretStr

from new_types import DodoIsApiConnectionHttpClient

__all__ = ('DodoISConnection',)


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
        return await self.__http_client.get(
            url=url,
            params=request_query_params,
            headers=headers,
        )

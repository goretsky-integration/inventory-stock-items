import httpx

from new_types import DodoISConnectionHttpClient

__all__ = ('DodoISConnection',)


class DodoISConnection:

    def __init__(self, http_client: DodoISConnectionHttpClient):
        self.__http_client = http_client

    def get_inventory_stocks(
            self,
            *,
            unit_id: int,
            cookies: dict[str, str],
    ) -> httpx.Response:
        url = '/OfficeManager/StockBalance/Get'
        request_query_params = {'unitId': unit_id}
        return self.__http_client.get(
            url=url,
            params=request_query_params,
            cookies=cookies,
        )

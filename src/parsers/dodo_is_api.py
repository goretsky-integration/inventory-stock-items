import httpx

from models import InventoryStocksResponseBody

__all__ = ('parse_inventory_stocks_response',)


def parse_inventory_stocks_response(
        response: httpx.Response,
) -> InventoryStocksResponseBody:
    response_data = response.json()
    return InventoryStocksResponseBody.model_validate(response_data)

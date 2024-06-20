import httpx

from enums import CategoryName
from filters import (
    filter_by_category_names,
    filter_relevant_items,
    filter_running_out_stock_items,
)
from models import InventoryStocksResponseBody

__all__ = ('parse_inventory_stocks_response',)


def parse_inventory_stocks_response(
        response: httpx.Response,
) -> InventoryStocksResponseBody:
    response_data = response.json()

    response_body = InventoryStocksResponseBody.model_validate(response_data)

    stocks = filter_relevant_items(
        items=response_body.stocks,
    )
    stocks = filter_running_out_stock_items(
        items=stocks,
        threshold=1,
    )
    allowed_category_names = (
        CategoryName.INVENTORY,
        CategoryName.PACKING,
        CategoryName.FINISHED_PRODUCT,
        CategoryName.SEMI_FINISHED_PRODUCT,
    )
    stocks = filter_by_category_names(
        items=stocks,
        category_names=allowed_category_names,
    )

    return InventoryStocksResponseBody(
        stocks=stocks,
        is_end_of_list_reached=response_body.is_end_of_list_reached,
    )

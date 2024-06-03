from typing import Annotated

from pydantic import BaseModel, Field

from models.inventory_stocks import InventoryStockItem

__all__ = ('InventoryStocksResponseBody',)


class InventoryStocksResponseBody(BaseModel):
    stocks: list[InventoryStockItem]
    is_end_of_list_reached: Annotated[
        bool,
        Field(validation_alias='isEndOfListReached'),
    ]

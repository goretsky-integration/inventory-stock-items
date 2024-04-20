from pydantic import BaseModel, Field, conlist

from models.inventory_stocks import InventoryStockItem

__all__ = ('Event', 'EventPayload')


class EventPayload(BaseModel):
    unit_name: str
    inventory_stock_items: list[InventoryStockItem]


class Event(BaseModel):
    type: str = Field(default='STOCKS_BALANCE', frozen=True)
    unit_ids: conlist(list[int], min_length=1)
    payload: EventPayload

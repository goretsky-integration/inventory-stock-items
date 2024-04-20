from pydantic import BaseModel

__all__ = ('InventoryStockItem',)


class InventoryStockItem(BaseModel):
    name: str
    unit_id: int
    quantity: float
    measurement_unit: str
    days_until_balance_runs_out: int

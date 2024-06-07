from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from enums import CategoryName, MeasurementUnit

__all__ = ('InventoryStockItem',)


class InventoryStockItem(BaseModel):
    name: str
    unit_uuid: Annotated[UUID, Field(validation_alias='unitId')]
    quantity: float
    measurement_unit: Annotated[
        MeasurementUnit,
        Field(validation_alias='measurementUnit'),
    ]
    category_name: Annotated[
        CategoryName,
        Field(validation_alias='categoryName'),
    ]
    days_until_balance_runs_out: Annotated[
        int,
        Field(validation_alias='daysUntilBalanceRunsOut'),
    ]
    calculated_at: Annotated[datetime, Field(validation_alias='calculatedAt')]

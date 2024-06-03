from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from enums import MeasurementUnit

__all__ = ('InventoryStockItem',)


class InventoryStockItem(BaseModel):
    name: str
    unit_id: Annotated[UUID, Field(validation_alias='unitId')]
    quantity: float
    measurement_unit: Annotated[
        MeasurementUnit,
        Field(validation_alias='measurementUnit'),
    ]
    days_until_balance_runs_out: Annotated[
        int,
        Field(validation_alias='daysUntilBalanceRunsOut'),
    ]
    calculated_at: Annotated[datetime, Field(validation_alias='calculatedAt')]

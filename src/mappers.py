from collections import defaultdict
from collections.abc import Iterable
from functools import cached_property
from typing import TypeVar
from uuid import UUID

from models import Event, EventPayload, InventoryStockItem, Unit

__all__ = (
    'group_by_unit_uuid',
    'map_inventory_stocks_to_events',
    'UnitsMapper',
    'AccountsUnitsMapper',
)

T = TypeVar('T')


def group_by_unit_uuid(items: Iterable[T]) -> dict[UUID, list[T]]:
    unit_uuid_to_items: defaultdict[UUID, list[T]] = defaultdict(list)
    for item in items:
        unit_uuid_to_items[item.unit_uuid].append(item)
    return dict(unit_uuid_to_items)


def map_inventory_stocks_to_events(
        inventory_stocks: Iterable[InventoryStockItem],
        units: Iterable[Unit],
) -> list[Event]:
    unit_uuid_to_inventory_stocks = group_by_unit_uuid(inventory_stocks)

    events: list[Event] = []
    for unit in units:
        items = unit_uuid_to_inventory_stocks.get(unit.uuid, [])

        event = Event(
            unit_ids=[unit.id],
            payload=EventPayload(
                unit_name=unit.name,
                inventory_stock_items=items,
            ),
        )
        events.append(event)
    return events


class UnitsMapper:

    def __init__(self, units: Iterable[Unit]):
        self.__units = tuple(units)

    @cached_property
    def uuids(self) -> set[UUID]:
        return {unit.uuid for unit in self.__units}


class AccountsUnitsMapper:

    def __init__(self, accounts_units: Iterable[AccountUnits]):
        self.accounts_units = tuple(accounts_units)

    @cached_property
    def account_names(self) -> set[str]:
        return {
            account_units.account_name
            for account_units in self.accounts_units
        }

    @cached_property
    def units(self) -> list[Unit]:
        return [
            unit
            for account_units in self.accounts_units
            for unit in account_units.units
        ]

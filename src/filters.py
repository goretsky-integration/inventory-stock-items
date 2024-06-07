from collections.abc import Iterable

from enums import CategoryName
from models import InventoryStockItem

__all__ = (
    'filter_running_out_stock_items',
    'filter_by_category_names',
    'filter_relevant_items',
)


def filter_relevant_items(
        items: Iterable[InventoryStockItem],
) -> list[InventoryStockItem]:
    return [
        item for item in items
        if '(не использовать)' not in item.name.lower()
    ]


def filter_running_out_stock_items(
        items: Iterable[InventoryStockItem],
        threshold: int,
) -> list[InventoryStockItem]:
    return [
        item for item in items
        if item.days_until_balance_runs_out <= threshold
    ]


def filter_by_category_names(
        items: Iterable[InventoryStockItem],
        category_names: Iterable[CategoryName],
) -> list[InventoryStockItem]:
    category_names = set(category_names)
    return [
        item for item in items
        if item.category_name in category_names
    ]

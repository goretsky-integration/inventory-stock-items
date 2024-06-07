from collections.abc import Iterable

from enums import CategoryName
from models import InventoryStockItem

__all__ = (
    'filter_running_out_stock_items',
    'filter_by_category_names',
    'filter_relevant_items',
)


def is_all_zero(*numbers: int | float) -> bool:
    return all(number == 0 for number in numbers)


def filter_relevant_items(
        items: Iterable[InventoryStockItem],
) -> list[InventoryStockItem]:
    relevant_items: list[InventoryStockItem] = []

    for item in items:
        if '(не использовать)' in item.name.lower():
            continue
        if is_all_zero(
            item.average_weekend_expense,
            item.average_weekday_expense,
            item.balance_in_money,
            item.quantity,
            item.days_until_balance_runs_out,
        ):
            continue

        relevant_items.append(item)

    return relevant_items


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

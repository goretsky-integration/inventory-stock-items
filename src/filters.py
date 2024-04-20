from collections.abc import Iterable
from typing import Protocol, TypeVar

__all__ = ('filter_running_out_stock_items',)


class HasDaysUntilBalanceRunsOut(Protocol):
    days_until_balance_runs_out: int


HasDaysUntilBalanceRunsOutT = TypeVar(
    'HasDaysUntilBalanceRunsOutT',
    bound=HasDaysUntilBalanceRunsOut,
)


def filter_running_out_stock_items(
        items: Iterable[HasDaysUntilBalanceRunsOutT],
        threshold: int,
) -> list[HasDaysUntilBalanceRunsOutT]:
    return [
        item for item in items
        if item.days_until_balance_runs_out <= threshold
    ]

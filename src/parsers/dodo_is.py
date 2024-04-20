import operator

import httpx
from bs4 import BeautifulSoup, Tag

from models import InventoryStockItem

__all__ = ('parse_inventory_stocks_response',)

first_second_and_last = operator.itemgetter(0, 1, -1)


def get_stripped_text(tag: Tag) -> str:
    return tag.text.strip()


def remove_whitespaces(text: str) -> str:
    return text.replace(' ', '')


def replace_commas_with_dots(text: str) -> str:
    return text.replace(',', '.')


def parse_inventory_stock_item(
        table_row: Tag,
        unit_id: int,
) -> InventoryStockItem | None:
    tds = [get_stripped_text(td) for td in table_row.find_all('td')]

    if len(tds) != 6:
        return None

    name, quantity, days_until_balance_runs_out = first_second_and_last(tds)

    if not days_until_balance_runs_out.isdigit():
        return None

    *name_parts, measurement_unit = name.split(',')
    name = ','.join(name_parts)
    measurement_unit = measurement_unit.strip()
    quantity = float(
        replace_commas_with_dots(
            remove_whitespaces(
                quantity.strip())))

    return InventoryStockItem(
        unit_id=unit_id,
        name=name,
        days_until_balance_runs_out=days_until_balance_runs_out,
        measurement_unit=measurement_unit,
        quantity=quantity,
    )


def parse_inventory_stocks_response(
        response: httpx.Response,
        unit_id: int,
) -> list[InventoryStockItem]:
    soup = BeautifulSoup(response.text, 'lxml')

    trs = soup.find('tbody').find_all('tr')
    stocks_balance: list[InventoryStockItem] = []

    for tr in trs:
        inventory_stock_item = parse_inventory_stock_item(tr, unit_id)
        if inventory_stock_item is not None:
            stocks_balance.append(inventory_stock_item)

    return stocks_balance

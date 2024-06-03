import asyncio
import itertools
import pathlib

import sentry_sdk
from fast_depends import Depends, inject
from toolz import groupby

from auth_credentials_storage import AuthCredentialsStorageConnection
from config import load_config_from_file
from dodo_is import DodoISConnection
from filters import filter_running_out_stock_items
from http_clients import (
    closing_auth_credentials_storage_connection_http_client,
    closing_dodo_is_connection_http_client,
)
from logger import init_logging
from message_queue import publish_events
from models import Event, EventPayload, InventoryStockItem, Unit
from parsers import (
    parse_account_cookies_response,
)
from units_storage import load_units


@inject
async def main(
        units: list[Unit] = Depends(load_units),
) -> None:
    init_logging()

    if config.sentry.is_enabled:
        sentry_sdk.init(
            dsn=config.sentry.dsn,
            traces_sample_rate=config.sentry.traces_sample_rate,
            profiles_sample_rate=config.sentry.profiles_sample_rate,
        )

    account_name_to_units = (
        itertools.groupby(
            iterable=units,
            key=lambda unit: unit.office_manager_account_name,
        )
    )

    inventory_stock_items: list[InventoryStockItem] = []

    with closing_auth_credentials_storage_connection_http_client(
            base_url=config.auth_credentials_storage_base_url,
    ) as http_client:

        with closing_dodo_is_connection_http_client(
                country_code=config.country_code,
        ) as dodo_is_connection_http_client:
            dodo_is_connection = DodoISConnection(
                http_client=dodo_is_connection_http_client,
            )

            auth_credentials_storage_connection = (
                AuthCredentialsStorageConnection(http_client=http_client)
            )
            for account_name, units_grouped_by_account_name in account_name_to_units:
                account_cookies_response = (
                    auth_credentials_storage_connection.get_cookies(
                        account_name=account_name,
                    )
                )
                account_cookies = parse_account_cookies_response(
                    response=account_cookies_response,
                )

                for unit in units_grouped_by_account_name:
                    stocks_balance_response = dodo_is_connection.get_inventory_stocks(
                        unit_id=unit.id,
                        cookies=account_cookies.cookies,
                    )
                    inventory_stock_items += parse_inventory_stocks_response(
                        response=stocks_balance_response,
                        unit_id=unit.id,
                    )
    inventory_stock_items = filter_running_out_stock_items(
        items=inventory_stock_items,
        threshold=1,
    )
    unit_id_to_inventory_stock_items: dict[
        int, list[InventoryStockItem]] = groupby(
        lambda item: item.unit_id,
        inventory_stock_items,
    )

    unit_ids_and_names: list[tuple[int, str]] = [
        (unit.id, unit.name) for unit in units
    ]

    events: list[Event] = []
    for unit_id, unit_name in unit_ids_and_names:
        items = unit_id_to_inventory_stock_items.get(unit_id, [])

        event = Event(
            unit_ids=[unit_id],
            payload=EventPayload(
                unit_name=unit_name,
                inventory_stock_items=items,
            ),
        )
        events.append(event)

    await publish_events(
        message_queue_url=config.message_queue_url,
        events=events,
    )


if __name__ == '__main__':
    asyncio.run(main())

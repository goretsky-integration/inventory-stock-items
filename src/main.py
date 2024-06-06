import asyncio
import itertools
import operator

import sentry_sdk
import toolz
from fast_depends import Depends, inject
from toolz import groupby

from config import Config, load_config_from_file
from connections.auth_credentials import AuthCredentialsStorageConnection
from context.auth_credentials import AuthCredentialsFetchUnitOfWork
from context.dodo_is_api import InventoryStocksFetchUnitOfWork
from dependencies.auth_credentials import \
    get_auth_credentials_storage_connection
from dependencies.dodo_is_api import get_dodo_is_api_connection
from dodo_is import DodoISConnection
from filters import filter_running_out_stock_items
from http_clients import (
    closing_dodo_is_connection_http_client,
)
from logger import init_logging
from message_queue import publish_events
from models import AccountUnits, Event, EventPayload, InventoryStockItem, Unit
from parsers import (
    parse_account_tokens_response,
)
from units_storage import load_units


@inject
async def main(
        accounts_units: list[AccountUnits] = Depends(load_units),
        config: Config = Depends(load_config_from_file),
        auth_credentials_storage_connection: (
                AuthCredentialsStorageConnection
        ) = Depends(get_auth_credentials_storage_connection),
        dodo_is_api_connection: DodoISConnection = Depends(
            get_dodo_is_api_connection,
        )
) -> None:
    init_logging()

    if config.sentry.is_enabled:
        sentry_sdk.init(
            dsn=config.sentry.dsn,
            traces_sample_rate=config.sentry.traces_sample_rate,
            profiles_sample_rate=config.sentry.profiles_sample_rate,
        )

    # account_name_to_units = (
    #     itertools.groupby(
    #         iterable=units,
    #         key=lambda unit: unit.office_manager_account_name,
    #     )
    # )

    account_names = {
        account_units.account_name for account_units in accounts_units
    }

    auth_credentials_fetch_unit_of_work = AuthCredentialsFetchUnitOfWork(
        connection=auth_credentials_storage_connection,
    )
    for account_name in account_names:
        auth_credentials_fetch_unit_of_work.register_task(account_name)

    account_tokens = await auth_credentials_fetch_unit_of_work.commit()
    account_name_to_access_token = {
        account_token.account_name: account_token.access_token
        for account_token in account_tokens
    }

    inventory_stocks_fetch_unit_of_work = InventoryStocksFetchUnitOfWork(
        connection=dodo_is_api_connection,
    )
    for account_units in accounts_units:
        unit_uuids = [unit.uuid for unit in account_units.units]
        access_token = account_name_to_access_token[account_units.account_name]
        inventory_stocks_fetch_unit_of_work.register_task(
            access_token=access_token,
            unit_uuids=unit_uuids,
        )

    inventory_stocks = await inventory_stocks_fetch_unit_of_work.commit()

    inventory_stocks = filter_running_out_stock_items(
        items=inventory_stocks,
        threshold=1,
    )
    unit_uuid_to_inventory_stocks: dict[int, list[InventoryStockItem]] = groupby(
        operator.attrgetter('unit_uuid'),
        inventory_stocks,
    )

    units = [
        unit
        for account_units in accounts_units
        for unit in account_units.units
    ]

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

    await publish_events(
        message_queue_url=config.message_queue_url,
        events=events,
    )


if __name__ == '__main__':
    asyncio.run(main())

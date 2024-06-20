import asyncio
import sys

import sentry_sdk
from fast_depends import Depends, inject

from config import Config, load_config_from_file
from connections.auth_credentials import AuthCredentialsStorageConnection
from connections.dodo_is_api import DodoISConnection
from context.auth_credentials import AuthCredentialsFetchUnitOfWork
from context.dodo_is_api import InventoryStocksFetchUnitOfWork
from dependencies.auth_credentials import (
    get_auth_credentials_storage_connection,
)
from dependencies.dodo_is_api import get_dodo_is_api_connection
from logger import setup_logging
from mappers import (
    AccountsUnitsMapper,
    UnitsMapper,
    map_inventory_stocks_to_events,
)
from message_queue import publish_events
from models import AccountUnits
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
    setup_logging()

    accounts_units_mapper = AccountsUnitsMapper(accounts_units)

    if config.sentry.is_enabled:
        sentry_sdk.init(
            dsn=config.sentry.dsn,
            traces_sample_rate=config.sentry.traces_sample_rate,
            profiles_sample_rate=config.sentry.profiles_sample_rate,
        )

    auth_credentials_fetch_unit_of_work = AuthCredentialsFetchUnitOfWork(
        connection=auth_credentials_storage_connection,
    )
    for account_name in accounts_units_mapper.account_names:
        auth_credentials_fetch_unit_of_work.register_task(account_name)

    account_tokens = await auth_credentials_fetch_unit_of_work.commit()
    account_name_to_access_token = {
        account_token.account_name: account_token.access_token
        for account_token in account_tokens
    }

    inventory_stocks_fetch_unit_of_work = InventoryStocksFetchUnitOfWork(
        connection=dodo_is_api_connection,
    )
    for account_units in accounts_units_mapper.accounts_units:
        units_mapper = UnitsMapper(account_units.units)
        access_token = account_name_to_access_token[account_units.account_name]
        inventory_stocks_fetch_unit_of_work.register_task(
            access_token=access_token,
            unit_uuids=units_mapper.uuids,
        )

    inventory_stocks_result = await inventory_stocks_fetch_unit_of_work.commit()

    events = map_inventory_stocks_to_events(
        inventory_stocks_result=inventory_stocks_result,
        units=accounts_units_mapper.units,
    )

    await publish_events(
        message_queue_url=config.message_queue_url,
        events=events,
    )


if __name__ == '__main__':
    asyncio.run(main())

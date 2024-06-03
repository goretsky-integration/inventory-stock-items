import contextlib

import httpx

from enums import CountryCode
from new_types import (
    AuthCredentialsStorageConnectionHttpClient,
    DodoIsApiConnectionHttpClient,
)

__all__ = (
    'closing_dodo_is_connection_http_client',
    'closing_auth_credentials_storage_connection_http_client',
)


@contextlib.contextmanager
def closing_dodo_is_connection_http_client(
        country_code: CountryCode,
        **kwargs,
) -> DodoIsApiConnectionHttpClient:
    base_url = f'https://officemanager.dodopizza.{country_code}'

    with httpx.Client(timeout=30, base_url=base_url, **kwargs) as http_client:
        yield DodoIsApiConnectionHttpClient(http_client)


@contextlib.contextmanager
def closing_auth_credentials_storage_connection_http_client(
        base_url: str,
        **kwargs,
) -> AuthCredentialsStorageConnectionHttpClient:
    with httpx.Client(timeout=30, base_url=base_url, **kwargs) as http_client:
        yield AuthCredentialsStorageConnectionHttpClient(http_client)

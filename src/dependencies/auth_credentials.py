import httpx
from fast_depends import Depends

from config import Config, load_config_from_file
from connections.auth_credentials import AuthCredentialsStorageConnection
from new_types import AuthCredentialsStorageConnectionHttpClient

__all__ = (
    'get_auth_credentials_storage_http_client',
    'get_auth_credentials_storage_connection',
)


async def get_auth_credentials_storage_http_client(
        config: Config = Depends(load_config_from_file),
) -> AuthCredentialsStorageConnectionHttpClient:
    async with httpx.AsyncClient(
            base_url=config.auth_credentials_storage_base_url
    ) as http_client:
        yield AuthCredentialsStorageConnectionHttpClient(http_client)


async def get_auth_credentials_storage_connection(
        http_client: AuthCredentialsStorageConnectionHttpClient = Depends(
            get_auth_credentials_storage_http_client
        ),
) -> AuthCredentialsStorageConnection:
    return AuthCredentialsStorageConnection(http_client)

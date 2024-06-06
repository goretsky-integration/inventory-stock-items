import httpx
from fast_depends import Depends

from config import Config, load_config_from_file
from dodo_is import DodoISConnection
from new_types import DodoIsApiConnectionHttpClient

__all__ = (
    'get_dodo_is_api_http_client',
    'get_dodo_is_api_connection',
)


async def get_dodo_is_api_http_client(
        config: Config = Depends(load_config_from_file),
) -> DodoIsApiConnectionHttpClient:
    base_url = f'https://api.dodois.io/dodopizza/{config.country_code}/'
    async with httpx.AsyncClient(base_url=base_url, timeout=60) as http_client:
        yield DodoIsApiConnectionHttpClient(http_client)


async def get_dodo_is_api_connection(
        http_client: DodoIsApiConnectionHttpClient = Depends(
            get_dodo_is_api_http_client
        ),
) -> DodoISConnection:
    return DodoISConnection(http_client)

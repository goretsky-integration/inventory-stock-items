import pathlib
import tomllib
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from enums import CountryCode

__all__ = ('load_config_from_file', 'Config')


@dataclass(frozen=True, slots=True)
class Config:
    timezone: ZoneInfo
    units_storage_base_url: str
    auth_credentials_storage_base_url: str
    country_code: CountryCode


def load_config_from_file(file_path: pathlib.Path) -> Config:
    config_text = file_path.read_text(encoding='utf-8')
    config = tomllib.loads(config_text)

    timezone = ZoneInfo(config['timezone'])
    units_storage_base_url: str = config['units_storage']['base_url']
    auth_credentials_storage_base_url: str = (
        config['auth_credentials_storage']['base_url']
    )
    country_code = CountryCode[config['country_code'].upper()]

    return Config(
        timezone=timezone,
        units_storage_base_url=units_storage_base_url,
        auth_credentials_storage_base_url=auth_credentials_storage_base_url,
        country_code=country_code,
    )

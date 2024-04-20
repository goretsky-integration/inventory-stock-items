import pathlib
import tomllib
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from enums import CountryCode

__all__ = ('load_config_from_file', 'Config')


@dataclass(frozen=True, slots=True)
class SentryConfig:
    is_enabled: bool
    dsn: str
    traces_sample_rate: float
    profiles_sample_rate: float


@dataclass(frozen=True, slots=True)
class Config:
    timezone: ZoneInfo
    units_storage_base_url: str
    auth_credentials_storage_base_url: str
    country_code: CountryCode
    message_queue_url: str
    sentry: SentryConfig


def load_config_from_file(file_path: pathlib.Path) -> Config:
    config_text = file_path.read_text(encoding='utf-8')
    config = tomllib.loads(config_text)

    timezone = ZoneInfo(config['timezone'])
    units_storage_base_url: str = config['units_storage']['base_url']
    auth_credentials_storage_base_url: str = (
        config['auth_credentials_storage']['base_url']
    )
    country_code = CountryCode[config['country_code'].upper()]
    message_queue_url = config['message_queue']['url']

    sentry_config = config['sentry']
    sentry = SentryConfig(
        is_enabled=sentry_config['is_enabled'],
        dsn=sentry_config['dsn'],
        traces_sample_rate=sentry_config['traces_sample_rate'],
        profiles_sample_rate=sentry_config['profiles_sample_rate'],
    )

    return Config(
        timezone=timezone,
        units_storage_base_url=units_storage_base_url,
        auth_credentials_storage_base_url=auth_credentials_storage_base_url,
        country_code=country_code,
        message_queue_url=message_queue_url,
        sentry=sentry,
    )

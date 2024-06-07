import pathlib
import tomllib
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from enums import CountryCode

__all__ = (
    'load_config_from_file',
    'Config',
    'SOURCE_DIR',
    'ACCOUNTS_UNITS_FILE_PATH',
    'CONFIG_FILE_PATH',
    'LOGGING_CONFIG_FILE_PATH',
)

SOURCE_DIR = pathlib.Path(__file__).parent
ACCOUNTS_UNITS_FILE_PATH = SOURCE_DIR.parent / 'accounts_units.json'
CONFIG_FILE_PATH = SOURCE_DIR.parent / 'config.toml'
LOGGING_CONFIG_FILE_PATH = SOURCE_DIR.parent / 'logging_config.json'


@dataclass(frozen=True, slots=True)
class SentryConfig:
    is_enabled: bool
    dsn: str
    traces_sample_rate: float
    profiles_sample_rate: float


@dataclass(frozen=True, slots=True)
class Config:
    timezone: ZoneInfo
    auth_credentials_storage_base_url: str
    country_code: CountryCode
    message_queue_url: str
    sentry: SentryConfig


def load_config_from_file(file_path: pathlib.Path = CONFIG_FILE_PATH) -> Config:
    config_text = file_path.read_text(encoding='utf-8')
    config = tomllib.loads(config_text)

    timezone = ZoneInfo(config['timezone'])
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
        auth_credentials_storage_base_url=auth_credentials_storage_base_url,
        country_code=country_code,
        message_queue_url=message_queue_url,
        sentry=sentry,
    )

from typing import NewType

import httpx

__all__ = (
    'AuthCredentialsStorageConnectionHttpClient',
    'DodoISConnectionHttpClient',
)

AuthCredentialsStorageConnectionHttpClient = (
    NewType('AuthCredentialsStorageConnectionHttpClient', httpx.Client)
)
DodoISConnectionHttpClient = NewType('DodoISConnectionHttpClient', httpx.Client)

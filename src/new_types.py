from typing import NewType

import httpx

__all__ = (
    'AuthCredentialsStorageConnectionHttpClient',
    'DodoIsApiConnectionHttpClient',
)

AuthCredentialsStorageConnectionHttpClient = (
    NewType('AuthCredentialsStorageConnectionHttpClient', httpx.Client)
)
DodoIsApiConnectionHttpClient = NewType(
    'DodoIsApiConnectionHttpClient',
    httpx.AsyncClient,
)

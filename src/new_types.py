from typing import NewType

import httpx

__all__ = (
    'AuthCredentialsStorageConnectionHttpClient',
    'DodoIsApiConnectionHttpClient',
)

AuthCredentialsStorageConnectionHttpClient = (
    NewType('AuthCredentialsStorageConnectionHttpClient', httpx.AsyncClient)
)
DodoIsApiConnectionHttpClient = NewType(
    'DodoIsApiConnectionHttpClient',
    httpx.AsyncClient,
)

import asyncio

from connections.auth_credentials import AuthCredentialsStorageConnection
from models import AccountTokens
from parsers import parse_account_tokens_response

__all__ = ('AuthCredentialsFetchUnitOfWork',)


class AuthCredentialsFetchUnitOfWork:

    def __init__(self, connection: AuthCredentialsStorageConnection):
        self.__connection = connection
        self.__account_names: list[str] = []

    def register_task(self, account_name: str) -> None:
        self.__account_names.append(account_name)

    async def _get_account_tokens(self, account_name: str) -> AccountTokens:
        response = await self.__connection.get_tokens(account_name)
        return parse_account_tokens_response(response)

    async def commit(self) -> list[AccountTokens]:
        tasks = [
            self._get_account_tokens(account_name)
            for account_name in self.__account_names
        ]
        responses: tuple[AccountTokens | Exception, ...] = (
            await asyncio.gather(*tasks, return_exceptions=True)
        )
        return [
            response
            for response in responses
            if not isinstance(response, Exception)
        ]

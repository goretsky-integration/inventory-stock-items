from pydantic import BaseModel, SecretStr

__all__ = ('AccountTokens',)


class AccountTokens(BaseModel):
    account_name: str
    access_token: SecretStr

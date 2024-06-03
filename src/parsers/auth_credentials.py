import httpx

from models import AccountTokens

__all__ = ('parse_account_cookies_response',)


def parse_account_cookies_response(response: httpx.Response) -> AccountTokens:
    response_data: dict[str, str] = response.json()
    return AccountTokens.model_validate(response_data)

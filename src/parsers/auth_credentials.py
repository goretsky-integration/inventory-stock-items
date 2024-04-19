import json

import httpx

__all__ = ('parse_accounts_response',)


def parse_accounts_response(response: httpx.Response) -> set[str]:
    try:
        response_data: list[dict[str, str]] = response.json()
    except json.JSONDecodeError:
        raise  # TODO raise a custom exception here
    return {
        account['name'] for account in response_data
        if account['name'].startswith('office_manager_')
    }

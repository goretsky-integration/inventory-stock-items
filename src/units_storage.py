import httpx
from pydantic import TypeAdapter

from models import Unit

__all__ = ('get_units',)


def get_units(*, base_url: str) -> list[Unit]:
    with httpx.Client(base_url=base_url) as http_client:
        response = http_client.get('/units/')

    response_data = response.json()
    type_adapter = TypeAdapter(list[Unit])
    return type_adapter.validate_python(response_data['units'])

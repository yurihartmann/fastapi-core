from typing import Any, Optional, Union

from starlette.requests import HTTPConnection, Request
from starlette_context.plugins.base import Plugin


class HeadersPlugin(Plugin):
    key: str = "headers"

    async def process_request(self, request: Union[Request, HTTPConnection]) -> Optional[Any]:
        return request.headers

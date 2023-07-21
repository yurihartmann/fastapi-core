from typing import Union, Optional, Any

from starlette.requests import Request, HTTPConnection
from starlette_context.plugins.base import Plugin


class HeadersPlugin(Plugin):
    key: str = "headers"

    async def process_request(self, request: Union[Request, HTTPConnection]) -> Optional[Any]:
        return request.headers

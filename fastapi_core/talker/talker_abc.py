from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union

from httpx import Response
from httpx._types import CookieTypes, HeaderTypes, QueryParamTypes, RequestFiles


class HTTPErrorTalker(Exception):
    def __init__(self, response: Response) -> None:
        self.response = response


class TalkerABC(ABC):
    @abstractmethod
    async def request(
        cls,
        method: str,
        url: str,
        json: Any = None,
        headers: HeaderTypes = None,
        params: QueryParamTypes = None,
        files: RequestFiles = None,
        cookies: CookieTypes = None,
        status_accepts: Union[List[int], Tuple[int], int] = None,
        max_requests: int = 3,
        time_between_retry: float = 0.2,  # milliseconds
        timeout_seg: float = 5.0,  # seconds
        **kwargs
    ) -> Response:
        """Not Implemented"""

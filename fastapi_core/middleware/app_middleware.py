from http import HTTPStatus

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi_core.utils.exceptions import InternalErrorSchema


class AppMiddleware(BaseHTTPMiddleware):
    def __init__(self, is_environment_local: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_environment_local = is_environment_local

    @staticmethod
    def add_access_control_allow_origin(response):
        response.headers["access-control-allow-origin"] = "*"

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            self.add_access_control_allow_origin(response=response)
            return response

        except Exception:
            logger.exception("Error in Application")

            response = JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content=InternalErrorSchema().dict(),
            )
            self.add_access_control_allow_origin(response=response)

            return response

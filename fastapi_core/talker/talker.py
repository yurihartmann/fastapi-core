from asyncio import sleep
from http import HTTPStatus
from typing import Any, List, Tuple, Union

from httpx import AsyncClient, Response, TimeoutException
from httpx._types import CookieTypes, HeaderTypes, QueryParamTypes, RequestFiles
from loguru import logger

from fastapi_core.talker.talker_abc import HTTPErrorTalker, TalkerABC


class Talker(TalkerABC):
    STATUS_ACCEPTS_DEFAULT: Tuple[int] = (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
        HTTPStatus.ACCEPTED,
        HTTPStatus.NON_AUTHORITATIVE_INFORMATION,
        HTTPStatus.NO_CONTENT,
        HTTPStatus.RESET_CONTENT,
        HTTPStatus.PARTIAL_CONTENT,
        HTTPStatus.MULTI_STATUS,
        HTTPStatus.ALREADY_REPORTED,
        HTTPStatus.IM_USED,
    )

    STATUS_SUPRESS_RETRY: Tuple[int] = (
        HTTPStatus.NOT_FOUND,
        HTTPStatus.UNPROCESSABLE_ENTITY,
        HTTPStatus.METHOD_NOT_ALLOWED,
    )

    @classmethod
    def __generate_log_in_exception(cls, exc):
        if isinstance(exc, HTTPErrorTalker):
            return f"HTTPErrorTalker(status_code={exc.response.status_code} content={exc.response.content})"

        elif isinstance(exc, TimeoutException):
            return "TimeoutException()"

    @classmethod
    async def request(
        cls,
        method: str,
        url: str,
        json: Any = None,
        headers: HeaderTypes = None,
        params: QueryParamTypes = None,
        files: RequestFiles = None,
        cookies: CookieTypes = None,
        status_accepts: Union[List[int], Tuple[int], int] = STATUS_ACCEPTS_DEFAULT,
        status_supress_retry: Union[List[int], Tuple[int], int] = STATUS_SUPRESS_RETRY,
        max_requests: int = 3,
        time_between_retry: float = 0.2,  # milliseconds
        timeout_seg: float = 5.0,  # seconds
        **kwargs,
    ) -> Response:
        """
        :raise: httpx.TimeoutException
        :raise: HTTPErrorTalker
        """
        logger.debug(
            f"Talker | Request< method={method} url={url} max_requests={max_requests} "
            f"time_between_retry={time_between_retry} timeout_seg={timeout_seg}>"
        )

        requests_counter = 1

        while 1:
            logger.debug(f"Talker | Making request (requests_counter={requests_counter}) ...")
            client = AsyncClient()

            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=timeout_seg,
                    headers=headers,
                    json=json,
                    files=files,
                    cookies=cookies,
                    **kwargs,
                )

                try:
                    logger.debug(f"Talker | Response [{response.status_code}] - Content: {response.content}")
                except Exception:
                    pass

                if isinstance(status_accepts, int) and response.status_code == status_accepts:
                    return response

                if (
                    isinstance(status_accepts, list) or isinstance(status_accepts, tuple)
                ) and response.status_code in status_accepts:
                    return response

                raise HTTPErrorTalker(response=response)

            except (HTTPErrorTalker, TimeoutException) as exc:
                exception_log = cls.__generate_log_in_exception(exc=exc)

                if isinstance(exc, HTTPErrorTalker) and exc.response.status_code in status_supress_retry:
                    logger.warning(exception_log)
                    raise

                if requests_counter >= max_requests:
                    logger.error(exception_log)
                    raise

                logger.info(exception_log)
                logger.info(f"Talker | Sleep for {time_between_retry} s")

            finally:
                await client.aclose()

            requests_counter += 1
            await sleep(time_between_retry)
            time_between_retry *= 2

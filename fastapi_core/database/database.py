from collections import defaultdict
from contextlib import asynccontextmanager
from enum import Enum
from typing import Callable, AsyncContextManager

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from fastapi_core.utils.app_dependencies_abc import AppDependenciesABC


class DatabaseRole(str, Enum):
    MASTER = "master"
    REAL_ONLY = "read_only"


class Database(AppDependenciesABC):
    _connections: dict[DatabaseRole, AsyncEngine] = defaultdict(lambda: {})

    def __init__(
        self,
        db_url: str,
        db_url_read_only: str = None,
        echo_queries: bool = False,
        *args,
        **kwargs,
    ) -> None:
        logger.info("Starting database...")
        logger.info(f"Connecting in {DatabaseRole.MASTER}...")
        self._connections[DatabaseRole.MASTER] = self.__init_engine(
            *args, db_url=db_url, echo_queries=echo_queries, **kwargs
        )

        if db_url_read_only:
            logger.info(f"Connecting in {DatabaseRole.REAL_ONLY}...")
            self._connections[DatabaseRole.REAL_ONLY] = self.__init_engine(
                *args, db_url=db_url_read_only, echo_queries=echo_queries, **kwargs
            )

        self.is_ready()

    @classmethod
    def __init_engine(cls, db_url: str, echo_queries: bool, *args, **kwargs) -> AsyncEngine:
        return create_async_engine(
            *args,
            db_url,
            echo=echo_queries,
            future=True,
            pool_pre_ping=True,
            poolclass=NullPool,
            **kwargs,
        )

    @classmethod
    def __init_async_session(cls, bind: AsyncEngine) -> AsyncSession:
        return AsyncSession(
            bind=bind,
            expire_on_commit=False,
        )

    def __has_read_only(self) -> bool:
        if self._connections.get(DatabaseRole.REAL_ONLY):
            return True
        return False

    def get_master_session(self) -> AsyncSession:
        return self.__init_async_session(self._connections[DatabaseRole.MASTER])

    def get_read_only_session(self) -> AsyncSession | None:
        if self.__has_read_only():
            return self.__init_async_session(self._connections[DatabaseRole.REAL_ONLY])
        return None

    @asynccontextmanager
    async def get_async_session_factory(self, read_only: bool = False) -> Callable[..., AsyncContextManager[AsyncSession]]:
        # """
        # Get AsyncSession in async context manager
        # :param read_only:
        # :return:  AsyncSession
        # """
        async_session = self.__init_async_session(
            bind=(
                self._connections[DatabaseRole.REAL_ONLY]
                if read_only and self.__has_read_only()
                else self._connections[DatabaseRole.MASTER]
            )
        )

        try:
            yield async_session
        except Exception:
            logger.exception("Error in Database.AsyncSession | Executing rollback ...")
            await async_session.rollback()
            raise
        finally:
            await async_session.close()

    async def is_ready(self) -> bool:
        try:
            async_session = self.get_master_session()
            await async_session.execute("SELECT 1;")

            async_session_read_only = self.get_read_only_session()
            if async_session_read_only:
                await async_session_read_only.execute("SELECT 1;")

            return True

        except Exception:
            logger.exception("Error in AsyncDatabase.is_ready")
            return False

    def __str__(self):
        return "Database"

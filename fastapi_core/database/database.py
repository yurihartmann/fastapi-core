from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import contextmanager
from enum import Enum

from loguru import logger
from sqlmodel import Session, create_engine


class DatabaseRole(str, Enum):
    MASTER = "master"
    REAL_ONLY = "read_only"


class SessionProvided(ABC):
    @abstractmethod
    def get_session_factory(self, read_only: bool = False) -> Session:
        """Not Implemented"""


class Database(SessionProvided):
    provided: SessionProvided
    _connections: dict[DatabaseRole, Session] = defaultdict(lambda: {})

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

    @classmethod
    def __init_engine(cls, db_url: str, echo_queries: bool, *args, **kwargs) -> Session:
        engine = create_engine(*args, db_url, echo=echo_queries, future=True, pool_pre_ping=True, **kwargs)
        return Session(bind=engine, expire_on_commit=False)

    def get_master_session(self) -> Session:
        return self._connections[DatabaseRole.MASTER]

    def get_read_only_session(self) -> Session:
        return self._connections[DatabaseRole.MASTER]

    # async def readiness(self) -> bool:
    #     try:
    #         await self.master_async_session.execute("SELECT 1;")
    #
    #         if self.read_only_async_session:
    #             await self.read_only_async_session.execute("SELECT 1;")
    #
    #         return True
    #
    #     except Exception:
    #         traceback.print_exc()
    #         return False

    @contextmanager
    def get_session_factory(self, read_only: bool = False) -> Session:
        session: Session = self._connections[DatabaseRole.MASTER]

        if read_only and self._connections.get(DatabaseRole.REAL_ONLY):
            session = self._connections[DatabaseRole.REAL_ONLY]

        try:
            yield session
        except Exception:
            logger.error("Error in Session - Executing rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()

    def __str__(self):
        return "Database"

import unittest
from unittest.mock import Mock

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_core.database import Database
from fastapi_core.database.database import DatabaseRole
from sqlmodel import Session


class TestDatabase(unittest.IsolatedAsyncioTestCase):
    async def test__str__(self):
        # Arrange
        db = Database(db_url="sqlite+aiosqlite://", db_url_read_only="sqlite+aiosqlite://")

        # Act and Assert
        self.assertEqual(str(db), "Database")

    async def test_get_session(self):
        # Arrange
        db_full = Database(db_url="sqlite+aiosqlite://", db_url_read_only="sqlite+aiosqlite://")

        # Act and Assert
        self.assertIsInstance(db_full.get_master_session(), AsyncSession)
        self.assertIsInstance(db_full.get_read_only_session(), AsyncSession)

    async def test_get_session_factory_with_only_master(self):
        # Arrange
        db_master = Database(db_url="sqlite+aiosqlite://")

        # Act and Assert
        async with db_master.get_async_session_factory() as session:
            self.assertIsInstance(session, AsyncSession)

    async def test_get_session_factory_with_master_and_read_only(self):
        # Arrange
        db_full = Database(db_url="sqlite+aiosqlite://", db_url_read_only="sqlite+aiosqlite://")

        # Act and Assert
        with db_full.get_async_session_factory() as session:
            self.assertIsInstance(session, Session)
            self.assertEqual(session, db_full._connections[DatabaseRole.MASTER])

        with db_full.get_async_session_factory(read_only=True) as session:
            self.assertIsInstance(session, Session)
            self.assertEqual(session, db_full._connections[DatabaseRole.REAL_ONLY])

    async def test_get_session_factory_with_error(self):
        # Arrange
        db_full = Database(db_url="sqlite+aiosqlite://")
        session_mock = Mock()
        db_full._connections[DatabaseRole.MASTER] = session_mock

        # Act and Assert
        with self.assertRaises(Exception) as _:
            async with db_full.factory_async_session_manager() as session:
                await session.delete()
                raise Exception

        session_mock.rollback.assert_called_once_with()

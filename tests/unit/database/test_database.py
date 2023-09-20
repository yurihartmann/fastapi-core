import unittest
from unittest.mock import patch, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_core.database import Database


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
        async with db_master.factory_async_session_manager() as session:
            self.assertIsInstance(session, AsyncSession)

    async def test_get_session_factory_with_master_and_read_only(self):
        # Arrange
        db_full = Database(db_url="sqlite+aiosqlite://", db_url_read_only="sqlite+aiosqlite://")

        # Act and Assert
        async with db_full.factory_async_session_manager() as session:
            self.assertIsInstance(session, AsyncSession)

        async with db_full.factory_async_session_manager(read_only=True) as session:
            self.assertIsInstance(session, AsyncSession)

    @patch("fastapi_core.database.database.AsyncSession")
    async def test_get_session_factory_with_error(self, async_session_class_mock):
        # Arrange
        db_full = Database(db_url="sqlite+aiosqlite://")
        async_session = Mock()
        async_session_class_mock.return_value = async_session
        # Act and Assert
        with self.assertRaises(Exception) as _:
            async with db_full.factory_async_session_manager() as session:
                await session.delete()
                raise Exception

        async_session.rollback.assert_called_once_with()

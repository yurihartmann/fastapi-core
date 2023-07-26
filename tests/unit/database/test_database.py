import unittest

from fastapi_core.database import Database
from fastapi_core.database.database import DatabaseRole
from sqlmodel import Session


class TestDatabase(unittest.IsolatedAsyncioTestCase):
    async def test_get_session_factory_with_only_master(self):
        # Arrange
        db_master = Database(db_url="sqlite://")

        # Act and Assert
        with db_master.get_session_factory() as session:
            self.assertIsInstance(session, Session)
            self.assertEqual(session, db_master._connections[DatabaseRole.MASTER])

    async def test_get_session_factory_with_master_and_read_only(self):
        # Arrange
        db_full = Database(db_url="sqlite://", db_url_read_only="sqlite://")

        # Act and Assert
        with db_full.get_session_factory() as session:
            self.assertIsInstance(session, Session)
            self.assertEqual(session, db_full._connections[DatabaseRole.MASTER])

        with db_full.get_session_factory(read_only=True) as session:
            self.assertIsInstance(session, Session)
            self.assertEqual(session, db_full._connections[DatabaseRole.REAL_ONLY])

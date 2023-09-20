import unittest
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from fastapi_core.database import Database
from fastapi_core.database.database import DatabaseRole
from fastapi_core.model import ModelMixin
from fastapi_core.repository import Repository


class MyModel(ModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class TestModelBase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.database = Database(db_url="sqlite+aiosqlite:///./test.db")

        async with self.database._connections[DatabaseRole.MASTER].begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

        self.repo = Repository(async_session_manager=self.database.factory_async_session_manager, model=MyModel)

    async def test_model_created(self):
        # Arrange
        model = MyModel(name="test")
        obj: MyModel = await self.repo.create(model)

        # Assert
        self.assertEqual(obj.name, "test")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsNone(obj.updated_at)
        self.assertIsNone(obj.deleted_at)

    async def test_model_updated(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))
        obj.name = "test2"
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test2")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)
        self.assertTrue(obj.created_at < obj.updated_at)
        self.assertIsNone(obj.deleted_at)

    async def test_model_soft_delete(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Act
        obj.soft_delete()
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)
        self.assertTrue(obj.created_at < obj.updated_at)
        self.assertIsInstance(obj.deleted_at, datetime)

        # Act
        obj.undo_soft_delete()
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)
        self.assertTrue(obj.created_at < obj.updated_at)
        self.assertIsNone(obj.deleted_at)

    async def test_model_update_values(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Assert
        self.assertEqual(obj.name, "test")

        # Act
        obj.update_values(name="test2")
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test2")

    async def test_model_update_values_ignore_fields_not_exist(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Assert
        self.assertEqual(obj.name, "test")

        # Act
        obj.update_values(name="test2", test=1, ignore_fields_not_exist=True)
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test2")

    async def test_model_update_values_with_wrong_field(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Assert
        self.assertEqual(obj.name, "test")

        # Act
        with self.assertRaises(ValueError) as _:
            obj.update_values(name="test2", test=1)

    async def test_model_update_values_from_dict(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Assert
        self.assertEqual(obj.name, "test")

        # Act
        obj.update_values_from_dict({"name": "test2"})
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test2")

    async def test_model_update_values_from_dict_ignore_fields_not_exist(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Assert
        self.assertEqual(obj.name, "test")

        # Act
        obj.update_values_from_dict({"name": "test2", "test": 1}, ignore_fields_not_exist=True)
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test2")

    async def test_model_update_values_from_dict_with_wrong_field(self):
        # Arrange
        obj: MyModel = await self.repo.create(MyModel(name="test"))

        # Assert
        self.assertEqual(obj.name, "test")

        # Act
        with self.assertRaises(ValueError) as _:
            obj.update_values_from_dict({"name": "test2", "test": 1})

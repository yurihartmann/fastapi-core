import unittest
from datetime import datetime
from typing import Optional

from fastapi_core.database import Database
from fastapi_core.model import ModelMixin
from fastapi_core.repository import Repository
from sqlmodel import Field, SQLModel


class MyModel(ModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class TestModelBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.database = Database(db_url="sqlite://")

        SQLModel.metadata.create_all(bind=self.database.get_master_session().bind)

        self.repo = Repository(session_factory=self.database.get_session_factory, model=MyModel)

    async def test_model_created(self):
        # Arrange
        model = MyModel(name="test")
        obj: MyModel = await self.repo.create(model)

        # Assert
        self.assertEqual(obj.name, "test")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsNone(obj.updated_at)
        self.assertIsNone(obj.delete_at)

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
        self.assertIsNone(obj.delete_at)

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
        self.assertIsInstance(obj.delete_at, datetime)

        # Act
        obj.undo_soft_delete()
        obj: MyModel = await self.repo.update(obj)

        # Assert
        self.assertEqual(obj.name, "test")
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)
        self.assertTrue(obj.created_at < obj.updated_at)
        self.assertIsNone(obj.delete_at)

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

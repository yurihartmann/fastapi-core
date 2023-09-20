from tests.unit.repository.test_repository import TestRepository


class TestCount(TestRepository):
    async def test_count(self):
        # Arrange
        await self.create_heroes(5)

        # Act
        count = await self.repo.count()

        # Assert
        self.assertIsInstance(count, int)
        self.assertEqual(5, count)

    async def test_count_that_return_zero(self):
        # Arrange
        await self.create_heroes(5)

        # Act
        count = await self.repo.count(filters={"name": "foo"})

        # Assert
        self.assertIsInstance(count, int)
        self.assertEqual(0, count)

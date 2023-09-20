from tests.unit.repository.hero_model import Hero, Power
from tests.unit.repository.test_repository import TestRepository


class TestFindAll(TestRepository):
    async def test_find_all_by_id(self):
        # Arrange
        await self.create_hero_with_powers(n_powers=2)
        await self.create_heroes(4)

        # Act
        heroes = await self.repo.find_all(filters={"id": 1}, relationship_to_load=["powers"])

        # Assert
        self.assertEqual(1, heroes[0].id)
        self.assertIsInstance(heroes[0], Hero)
        self.assertIsInstance(heroes, list)
        self.assertEqual(1, len(heroes))
        self.assertEqual(2, len(heroes[0].powers))
        self.assertIsInstance(heroes[0].powers[0], Power)

    async def test_find_all_without_filter(self):
        # Arrange
        await self.create_heroes(5)

        # Act
        heroes = await self.repo.find_all()

        # Assert
        self.assertIsInstance(heroes[0], Hero)
        self.assertIsInstance(heroes, list)
        self.assertEqual(5, len(heroes))

    async def test_find_all_that_return_none(self):
        # Act
        heroes = await self.repo.find_all(filters={"id": 1})

        # Assert
        self.assertEqual(0, len(heroes))
        self.assertIsInstance(heroes, list)

    async def test_find_all_by_id_with_desc(self):
        # Arrange
        await self.create_heroes(3)

        # Act
        heroes = await self.repo.find_all(desc=True, order_by="id")

        # Assert
        self.assertEqual(3, heroes[0].id)
        self.assertEqual(2, heroes[1].id)
        self.assertEqual(1, heroes[2].id)
        self.assertIsInstance(heroes[0], Hero)
        self.assertIsInstance(heroes, list)
        self.assertEqual(3, len(heroes))

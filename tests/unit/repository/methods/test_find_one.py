from tests.unit.repository.hero_model import Hero, Power
from tests.unit.repository.test_repository import TestRepository


class TestFindOne(TestRepository):
    async def test_find_one_with_id_filter(self):
        # Arrange
        create_heroes = await self.create_heroes(n=3)

        # Act
        hero: Hero = await self.repo.find_one(filters={"id": 1})

        # Assert
        self.assertEqual(hero.id, 1)
        self.assertEqual(hero.name, create_heroes[0].name)

    async def test_find_one_with_order_by(self):
        # Arrange
        create_heroes = await self.create_heroes(n=3)

        # Act
        hero: Hero = await self.repo.find_one(order_by="id")

        # Assert
        self.assertEqual(hero.id, 1)
        self.assertEqual(hero.name, create_heroes[0].name)

    async def test_find_one_with_order_by_desc(self):
        # Arrange
        create_heroes = await self.create_heroes(n=3)

        # Act
        hero: Hero = await self.repo.find_one(order_by="id", desc=True)

        # Assert
        self.assertEqual(hero.id, 3)
        self.assertEqual(hero.name, create_heroes[2].name)

    async def test_find_one_that_return_none(self):
        # Act
        hero = await self.repo.find_one(filters={"id": 1})

        # Assert
        self.assertIsNone(hero)

    async def test_find_one_with_keys_subquery_load(self):
        # Assert
        await self.create_heroes(n=1)
        await self.create_hero_with_powers(n_powers=2)

        # Act
        hero = await self.repo.find_one(relationship_to_load=["powers"], order_by="id", desc=True)

        # Assert
        self.assertIsInstance(hero, Hero)
        self.assertIsInstance(hero.powers, list)
        self.assertIsInstance(hero.powers[1], Power)
        self.assertEqual(2, len(hero.powers))
        self.assertEqual(2, hero.id)

    async def test___sanitize_filters_from_model_do_not_exists(self):
        # Arrange
        await self.create_heroes(1)

        # Act
        hero = await self.repo.find_one(filters={"boo": 1})

        # Assert
        self.assertIsInstance(hero, Hero)

    async def test___sanitize_filters_from_model_that_no_is_dict(self):
        # Act and Assert
        with self.assertRaises(ValueError):
            await self.repo.find_one(filters=["boo"])

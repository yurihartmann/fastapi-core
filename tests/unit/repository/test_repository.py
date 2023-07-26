import unittest

from faker import Faker
from fastapi_core.database import Database
from fastapi_core.repository import Repository
from sqlmodel import SQLModel

from tests.unit.repository.hero_model import Hero, Power


class HeroRepository(Repository):
    def __init__(self, session_factory):
        super().__init__(session_factory, model=Hero)


class TestAsyncBaseRepository(unittest.IsolatedAsyncioTestCase):
    async def setUp(self) -> None:
        self.faker = Faker()
        self.database = Database(db_url="sqlite://")

        async with self.database.get_master_session().begin() as con:
            con.run(SQLModel.metadata.create_all)

        self.repo = HeroRepository(session_factory=self.database.get_session_factory)
        self.session = self.database.get_session_factory()

    def create_heroes(self, n: int = 3):
        for _ in range(n):
            self.session.add(Hero(name=self.faker.name()))

        self.session.commit()

    def create_hero_with_powers(self, n_powers: int = 0) -> Hero:
        hero = Hero(name=self.faker.name())

        for _ in range(n_powers):
            hero.powers.append(Power(name=self.faker.name()))
        self.session.add(hero)
        self.session.commit()
        self.session.refresh(hero)
        return hero

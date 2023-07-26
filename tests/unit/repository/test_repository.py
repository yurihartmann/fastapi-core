import unittest

from faker import Faker
from fastapi_core.database import Database
from fastapi_core.repository import Repository
from sqlmodel import SQLModel

from tests.unit.repository.hero_model import Hero, Power

faker = Faker()


class HeroRepository(Repository):
    def __init__(self, session_factory):
        super().__init__(session_factory, model=Hero)


class TestRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.database = Database(db_url="sqlite://")

        SQLModel.metadata.create_all(bind=self.database.get_master_session().bind)

        self.repo = HeroRepository(session_factory=self.database.get_session_factory)

    def create_heroes(self, n: int = 3) -> list[Hero]:
        with self.database.get_session_factory() as session:
            herois = [Hero(name=faker.name()) for _ in range(n)]
            for h in herois:
                session.add(h)
            session.commit()
            for h in herois:
                session.refresh(h)
            return herois

    def create_hero_with_powers(self, n_powers: int = 0) -> Hero:
        with self.database.get_session_factory() as session:
            hero = Hero(name=faker.name())

            for _ in range(n_powers):
                hero.powers.append(Power(name=faker.name()))
            session.add(hero)
            session.commit()
            session.refresh(hero)
            return hero

import unittest

from faker import Faker
from sqlmodel import SQLModel

from fastapi_core.database import Database
from fastapi_core.database.database import DatabaseRole
from fastapi_core.repository import Repository
from tests.unit.repository.hero_model import Hero, Power

faker = Faker()


class HeroRepository(Repository):
    def __init__(self, async_session_manager):
        super().__init__(async_session_manager, model=Hero)


class TestRepository(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.database = Database(db_url="sqlite+aiosqlite:///./test.db")

        async with self.database._connections[DatabaseRole.MASTER].begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

        self.repo = Repository(async_session_manager=self.database.factory_async_session_manager, model=Hero)

    async def create_heroes(self, n: int = 3) -> list[Hero]:
        async with self.database.factory_async_session_manager() as session:
            herois = [Hero(name=faker.name()) for _ in range(n)]
            for h in herois:
                session.add(h)
            await session.commit()
            for h in herois:
                await session.refresh(h)
            return herois

    async def create_hero_with_powers(self, n_powers: int = 0) -> Hero:
        async with self.database.factory_async_session_manager() as session:
            hero = Hero(name=faker.name())

            for _ in range(n_powers):
                hero.powers.append(Power(name=faker.name()))
            session.add(hero)
            await session.commit()
            await session.refresh(hero)
            return hero

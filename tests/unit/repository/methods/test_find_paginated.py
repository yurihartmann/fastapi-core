from fastapi_pagination import Params

from tests.unit.repository.hero_model import Power
from tests.unit.repository.test_repository import TestRepository


class TestFindPaginated(TestRepository):
    async def test_find_paginated_should_be_return_pagination_result(self):
        # Arrange
        self.create_heroes(10)

        # Act
        pagination_result = await self.repo.find_paginated(params=Params(page=1, size=3))

        # Assert
        self.assertEqual(10, pagination_result.total)
        self.assertEqual(3, len(pagination_result.items))
        self.assertEqual(1, pagination_result.items[0].id)
        self.assertEqual(2, pagination_result.items[1].id)
        self.assertEqual(3, pagination_result.items[2].id)

    async def test_find_paginated_with_relationship_to_load_should_be_return_pagination_result(self):
        # Arrange
        self.create_heroes(9)
        self.create_hero_with_powers(n_powers=2)

        # Act
        pagination_result = await self.repo.find_paginated(
            params=Params(page=1, size=3), order_by="id", desc=True, relationship_to_load=["powers"]
        )

        # Assert
        self.assertEqual(10, pagination_result.total)
        self.assertEqual(3, len(pagination_result.items))
        self.assertEqual(10, pagination_result.items[0].id)
        self.assertEqual(9, pagination_result.items[1].id)
        self.assertEqual(8, pagination_result.items[2].id)
        self.assertEqual(2, len(pagination_result.items[0].powers))
        self.assertIsInstance(pagination_result.items[0].powers[0], Power)

    async def test_find_paginated_should_be_return_pagination_result_with_desc(self):
        # Arrange
        self.create_heroes(10)

        # Act
        pagination_result = await self.repo.find_paginated(params=Params(page=1, size=3), desc=True, order_by="id")

        # Assert
        self.assertEqual(10, pagination_result.total)
        self.assertEqual(3, len(pagination_result.items))
        self.assertEqual(10, pagination_result.items[0].id)
        self.assertEqual(9, pagination_result.items[1].id)
        self.assertEqual(8, pagination_result.items[2].id)

    async def test_find_paginated_should_be_return_pagination_result_with_offset(self):
        # Arrange
        self.create_heroes(6)

        # Act
        pagination_result = await self.repo.find_paginated(params=Params(page=2, size=3))

        # Assert
        self.assertEqual(6, pagination_result.total)
        self.assertEqual(3, len(pagination_result.items))
        self.assertEqual(4, pagination_result.items[0].id)
        self.assertEqual(5, pagination_result.items[1].id)
        self.assertEqual(6, pagination_result.items[2].id)

    async def test_find_paginated_should_be_raise_params_value_error(self):
        # Arrange
        self.create_heroes(6)

        # Act and Assert
        with self.assertRaises(ValueError):
            await self.repo.find_paginated(params={"size": 3})

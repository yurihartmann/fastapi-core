from abc import ABC

from sqlmodel import SQLModel
from sqlmodel.sql.expression import SelectOfScalar

from fastapi_pagination import Params, Page


class RepositoryABC(ABC):
    def _add_subquery_load(self, query: SelectOfScalar, keys_subquery_load: list[str]) -> SelectOfScalar:
        """Not Implemented"""

    def _add_joined_load(self, query: SelectOfScalar, keys_joined_load: list[str]) -> SelectOfScalar:
        """Not Implemented"""

    async def _sanitize_filters_from_model(self, filters: dict) -> dict:
        """Not Implemented"""

    async def find_one_by_filters(
        self,
        filters: dict[str, any] = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> SQLModel | None:
        """Not Implemented"""

    async def find_by_filters_paginated(
        self,
        params: Params = Params(),
        filters: dict = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> Page[SQLModel]:
        """Not Implemented"""

    async def find_all_by_filters(
        self, filters: dict = None, order_by: str = None, desc: bool = False, relationship_to_load: list[str] = None
    ) -> list[SQLModel]:
        """Not Implemented"""

    async def count_by_filters(self, filters: dict = None) -> int:
        """Not Implemented"""

    async def create(self, obj: dict[str, any] | SQLModel) -> SQLModel:
        """Not Implemented"""

    async def bulk_create(self, objs: list[dict[str, any] | SQLModel]) -> list[SQLModel]:
        """Not Implemented"""

    async def update(self, obj: SQLModel, update_values: dict[str, any] | SQLModel = None) -> SQLModel:
        """Not Implemented"""

    async def bulk_update(self, objs: list[SQLModel]) -> list[SQLModel]:
        """Not Implemented"""

    async def delete(self, obj: SQLModel) -> None:
        """Not Implemented"""

    async def bulk_delete(self, objs: list[SQLModel]) -> None:
        """Not Implemented"""

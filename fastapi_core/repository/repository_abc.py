from abc import ABC, abstractmethod
from typing import TypeVar

from fastapi_pagination import Page, Params
from sqlmodel import SQLModel
from sqlmodel.sql.expression import SelectOfScalar

Model = TypeVar("Model", bound=SQLModel)


class RepositoryABC(ABC):

    @abstractmethod
    def _add_subquery_load(self, query: SelectOfScalar, keys_subquery_load: list[str]) -> SelectOfScalar:
        """Not Implemented"""

    @abstractmethod
    def _add_joined_load(self, query: SelectOfScalar, keys_joined_load: list[str]) -> SelectOfScalar:
        """Not Implemented"""

    @abstractmethod
    async def _sanitize_filters_from_model(self, filters: dict) -> dict:
        """Not Implemented"""

    @abstractmethod
    async def find_one(
        self,
        filters: dict[str, any] = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> Model | None:
        """Not Implemented"""

    @abstractmethod
    async def find_paginated(
        self,
        params: Params = Params(),
        filters: dict = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> Page[Model]:
        """Not Implemented"""

    @abstractmethod
    async def find_all(
        self,
        filters: dict = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> list[Model]:
        """Not Implemented"""

    @abstractmethod
    async def count(self, filters: dict = None) -> int:
        """Not Implemented"""

    @abstractmethod
    async def create(self, obj: dict[str, any] | SQLModel) -> Model:
        """Not Implemented"""

    @abstractmethod
    async def bulk_create(self, objs: list[dict[str, any] | SQLModel]) -> list[Model]:
        """Not Implemented"""

    @abstractmethod
    async def update(self, obj: SQLModel, update_values: dict[str, any] | SQLModel = None) -> Model:
        """Not Implemented"""

    @abstractmethod
    async def bulk_update(self, objs: list[SQLModel]) -> list[Model]:
        """Not Implemented"""

    @abstractmethod
    async def delete(self, obj: SQLModel) -> None:
        """Not Implemented"""

    @abstractmethod
    async def bulk_delete(self, objs: list[SQLModel]) -> None:
        """Not Implemented"""

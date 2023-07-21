from abc import ABC

from fastapi_pagination import Params, Page
from sqlmodel import SQLModel

from fastapi_core.model import ModelMixin
from fastapi_core.repository import RepositoryABC
from fastapi_core.utils.exceptions import EntityNotFoundException


class Service(ABC):
    def __init__(self, repository: RepositoryABC, pk_field: any):
        self.repository = repository
        self.pk_field = pk_field

    async def get_by_pk(self, pk: any, raise_exception_that_not_exist: bool = True) -> ModelMixin | SQLModel:
        if obj := await self.repository.find_one_by_filters(filters={self.pk_field: pk}):
            return obj

        if raise_exception_that_not_exist:
            raise EntityNotFoundException

    async def get_paginated(self, params: Params, filters: dict = None) -> Page:
        return await self.repository.find_by_filters_paginated(params=params, filters=filters)

    async def create(self, obj: SQLModel) -> SQLModel:
        return await self.repository.create(obj=obj)

    async def update(self, pk: any, obj_update: SQLModel) -> SQLModel:
        db_obj = await self.get_by_pk(pk=pk)
        return await self.repository.update(obj=db_obj, update_values=obj_update)

    async def delete(self, pk: any) -> None:
        db_obj = await self.get_by_pk(pk=pk)
        return await self.repository.delete(obj=db_obj)

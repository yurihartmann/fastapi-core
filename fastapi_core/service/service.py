from typing import TypeVar

from fastapi_pagination import Page, Params
from pydantic import BaseModel
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import SQLModel

from fastapi_core.model import ModelMixin
from fastapi_core.repository import RepositoryABC
from fastapi_core.utils.exceptions import EntityNotFoundException

T = TypeVar("T")


class Service:
    def __init__(self, repository: RepositoryABC, pk_field: str | InstrumentedAttribute):
        self.repository = repository
        self.pk_field = pk_field.key if isinstance(pk_field, InstrumentedAttribute) else pk_field

    async def get_by_pk(self, pk: any, raise_exception_that_not_exist: bool = True) -> ModelMixin | SQLModel | T:
        if obj := await self.repository.find_one(filters={self.pk_field: pk}):
            return obj

        if raise_exception_that_not_exist:
            raise EntityNotFoundException

    async def get_paginated(self, params: Params, filters: dict = None) -> Page:
        return await self.repository.find_paginated(params=params, filters=filters)

    async def create(self, obj: SQLModel | BaseModel) -> ModelMixin | SQLModel | T:
        return await self.repository.create(obj=obj)

    async def update(self, pk: any, obj_update: SQLModel | BaseModel | dict) -> ModelMixin | SQLModel | T:
        db_obj = await self.get_by_pk(pk=pk)
        return await self.repository.update(obj=db_obj, update_values=obj_update)

    async def delete(self, pk: any) -> None:
        db_obj = await self.get_by_pk(pk=pk)
        return await self.repository.delete(obj=db_obj)

    async def soft_delete(self, pk: any) -> ModelMixin | SQLModel | T:
        obj = await self.get_by_pk(pk=pk)
        obj.soft_delete()
        return await self.repository.update(obj)

    async def undo_soft_delete(self, pk: any) -> ModelMixin | SQLModel | T:
        obj = await self.get_by_pk(pk=pk)
        obj.undo_soft_delete()
        return await self.repository.update(obj)

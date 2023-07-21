from abc import ABC
from typing import Callable

from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Params, Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.orm import subqueryload, joinedload
from sqlmodel import Session, select, desc as descending, func, SQLModel
from sqlmodel.sql.expression import SelectOfScalar

from fastapi_core.repository.repository_abc import RepositoryABC


class Repository(RepositoryABC, ABC):
    def __init__(self, session_factory: Callable[..., Session], model: type[SQLModel]):
        """
        The constructor received the session and the model of repository
        :param session_factory: The session of SQLModel or sqlalchemy
        :param model: The model of repository, example: UserModel, ItemModel
        """
        self.session_factory = session_factory
        self.model = model

    def _add_subquery_load(self, query: SelectOfScalar, keys_subquery_load: list[str]) -> SelectOfScalar:
        for key in keys_subquery_load:
            query = query.options(subqueryload(getattr(self.model, key)))

        return query

    def _add_joined_load(self, query: SelectOfScalar, keys_joined_load: list[str]) -> SelectOfScalar:
        for key in keys_joined_load:
            query = query.options(joinedload(getattr(self.model, key)))

        return query

    def _sanitize_filters_from_model(self, filters: dict) -> dict:
        """
        This method received the filters for query and check if field have in model passed in constructor
        and if you do not exist in model remove
        :param filters: A dict with filters, example {'id': 1, 'name': 'foo'}
        :return: return the filters dict with only correct filters
        """
        if not isinstance(filters, dict):
            raise ValueError(f"filters should be a dict, received {type(filters)}")

        keys = list(filters.keys())
        for key in keys:
            try:
                getattr(self.model, key)
            except AttributeError:
                del filters[key]

        return filters

    async def find_one_by_filters(
        self,
        filters: dict[str, any] = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> SQLModel | None:
        """
        This method make query using params, filters
        :param filters:
        :param order_by:
        :param desc:
        :param relationship_to_load:
        :return: The object ModelType | None
        """
        with self.session_factory() as session:
            filters = self._sanitize_filters_from_model(filters=filters) if filters else {}
            query = select(self.model).filter_by(**filters)

            if relationship_to_load:
                query = self._add_subquery_load(query=query, keys_subquery_load=relationship_to_load)

            if order_by and hasattr(self.model, order_by):
                query = query.order_by(descending(order_by)) if desc else query.order_by(order_by)

            return session.scalar(query)

    async def find_by_filters_paginated(
        self,
        params: Params = Params(),
        filters: dict = None,
        order_by: str = None,
        desc: bool = False,
        relationship_to_load: list[str] = None,
    ) -> Page[SQLModel]:
        """
        This method make query using params, filters, order and desc applied
        :param params: The obj Params (page and size)
        :param filters: A dict with filters, example {'id': 1, 'name': 'foo'}
        :param order_by: The field for ordering select in database
        :param desc: When False the select is using ASC, when True the select is using DESC
        :param relationship_to_load:
        :return: The object PaginationResult(items and count)
                items: The data of select
                count: with count of items for the filters
        """
        if not isinstance(params, Params):
            raise ValueError(f"params should be a Params obj, received {type(params)}")

        with self.session_factory() as session:
            filters = self._sanitize_filters_from_model(filters=filters) if filters else {}

            query = select(self.model)

            if relationship_to_load:
                query = self._add_joined_load(query=query, keys_joined_load=relationship_to_load)

            query = query.filter_by(**filters)
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(descending(order_by)) if desc else query.order_by(order_by)

            return paginate(session=session, query=query, params=params)

    async def find_all_by_filters(
        self, filters: dict = None, order_by: str = None, desc: bool = False, relationship_to_load: list[str] = None
    ) -> list[SQLModel]:
        """
        This method make query using params, filters, order and desc applied
        :param filters: A dict with filters, example {'id': 1, 'name': 'foo'}
        :param order_by: The field for ordering select in database
        :param desc: When False the select is using ASC, when True the select is using DESC
        :param relationship_to_load:
        :return: Return a list of Models
        """
        with self.session_factory() as session:
            filters = self._sanitize_filters_from_model(filters=filters) if filters else {}
            query = select(self.model)

            if relationship_to_load:
                query = self._add_joined_load(query=query, keys_joined_load=relationship_to_load)

            query = query.filter_by(**filters)

            if order_by and hasattr(self.model, order_by):
                query = query.order_by(descending(order_by)) if desc else query.order_by(order_by)

            return session.scalars(query).unique().all()

    async def __count_by_filters_query(self, filters: dict) -> int | None:
        """
        Rerturn count of query
        :param filters:
        :return: int
        """
        with self.session_factory() as session:
            query = select([func.count()]).select_from(self.model).filter_by(**filters)
            return session.scalar(query).first()

    async def count_by_filters(self, filters: dict = None) -> int:
        """
        This method count items with filters
        :param filters: A dict with filters, example {'id': 1, 'name': 'foo'}
        :return: Return int that represent the count of query
        """
        filters = self._sanitize_filters_from_model(filters=filters) if filters else {}
        return await self.__count_by_filters_query(filters=filters)

    def __create_new_obj(self, obj: dict[str, any] | SQLModel) -> SQLModel:
        if isinstance(obj, SQLModel):
            return obj

        if isinstance(obj, dict):
            new_obj = self.model()

            for field in obj:
                if field in obj:
                    setattr(new_obj, field, obj[field])

            return new_obj

        payload = jsonable_encoder(obj)
        return self.model(**payload)

    async def create(self, obj: dict[str, any] | SQLModel) -> SQLModel:
        """
        This method create object in database
        :param obj: The BaseModel with field and data or dict of data
        :return: The Model created
        """
        new_obj = self.__create_new_obj(obj=obj)
        with self.session_factory() as session:
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)
            return new_obj

    async def bulk_create(self, objs: list[dict[str, any] | SQLModel]) -> list[SQLModel]:
        """
        This method create objects in database
        :param objs:
        :return:
        """
        new_objs = [self.__create_new_obj(obj=obj) for obj in objs]
        with self.session_factory() as session:
            for new_obj in new_objs:
                session.add(new_obj)

            session.commit()

            for new_obj in new_objs:
                session.refresh(new_obj)

            return new_objs

    @classmethod
    def __update_obj(cls, obj: SQLModel, update_values: dict[str, any] | SQLModel = None) -> SQLModel:
        if isinstance(obj, SQLModel) and update_values is None:
            return obj

        obj_data = jsonable_encoder(obj)

        if isinstance(update_values, dict):
            update_data = update_values
        else:
            update_data = update_values.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(obj, field, update_data[field])

        return obj

    async def update(self, obj: SQLModel, update_values: dict[str, any] | SQLModel = None) -> SQLModel:
        """
        This method update the model in database
        :param obj: The Model in a database
        :param update_values: The BaseModel with field and data
        :return: The Model updated
        """
        obj_to_update = self.__update_obj(obj=obj, update_values=update_values)
        with self.session_factory() as session:
            obj_to_save = session.merge(obj_to_update)
            session.add(obj_to_save)
            session.commit()
            session.refresh(obj_to_save)
            return obj_to_save

    async def bulk_update(self, objs: list[SQLModel]) -> list[SQLModel]:
        """
        This method update the models in database
        :param objs:
        :return:
        """
        objs_to_update = [self.__update_obj(obj=obj) for obj in objs]
        with self.session_factory() as session:
            objs_to_save = []
            for obj_to_update in objs_to_update:
                objs_to_save.append(session.merge(obj_to_update))

            for obj_to_save in objs_to_save:
                session.add(obj_to_save)

            session.commit()

            for obj_to_save in objs_to_save:
                session.refresh(obj_to_save)

            return objs_to_save

    async def delete(self, obj: SQLModel) -> None:
        """
        This method delete item in database
        :param obj: The Model that will be deleted
        :return: The result of commit
        """
        with self.session_factory() as session:
            session.delete(obj)
            session.commit()

    async def bulk_delete(self, objs: list[SQLModel]) -> None:
        """
        This method delete item in database
        :param objs: The list of models that will be deleted
        :return: The result of commit
        """
        if not objs:
            return

        with self.session_factory() as session:
            for obj in objs:
                session.delete(obj)
            session.commit()

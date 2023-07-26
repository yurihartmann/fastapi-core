from typing import List, Optional

from fastapi_core.model import ModelMixin
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class Power(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hero_id: int = Field(foreign_key="hero.id")

    hero: List["Hero"] = Relationship(back_populates="powers")


class Hero(ModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    powers: List[Power] = Relationship(back_populates="hero", sa_relationship_kwargs={"lazy": "select"})


class CreateHero(BaseModel):
    name: str


class UpdateHero(CreateHero):
    pass

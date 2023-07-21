from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field


class ModelBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime, onupdate=datetime.now))
    delete_at: datetime | None = Field(default=None, nullable=True)

    def soft_delete(self):
        self.delete_at = datetime.now()

    def undo_soft_delete(self):
        self.delete_at = None

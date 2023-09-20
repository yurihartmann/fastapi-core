from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class ModelBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime, onupdate=datetime.now))
    deleted_at: datetime | None = Field(default=None, nullable=True)

    def soft_delete(self):
        if self.deleted_at:
            return

        self.deleted_at = datetime.now()

    def undo_soft_delete(self):
        self.deleted_at = None

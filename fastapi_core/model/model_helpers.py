from sqlmodel import SQLModel


class ModelHelpers(SQLModel):
    def update_values(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_values_from_dict(self, update: dict):
        for key, value in update.items():
            setattr(self, key, value)

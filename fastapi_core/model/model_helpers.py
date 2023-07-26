from sqlmodel import SQLModel


class ModelHelpers(SQLModel):
    def update_values(self, ignore_fields_not_exist: bool = False, **kwargs):
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except ValueError:
                if ignore_fields_not_exist:
                    continue
                else:
                    raise

    def update_values_from_dict(self, update: dict, ignore_fields_not_exist: bool = False):
        for key, value in update.items():
            try:
                setattr(self, key, value)
            except ValueError:
                if ignore_fields_not_exist:
                    continue
                else:
                    raise

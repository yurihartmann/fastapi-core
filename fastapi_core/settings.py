from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    ...


class AppSettings(Settings):
    ENVIRONMENT: str = Field(default="local", env="ENVIRONMENT")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        if v not in ["local", "dev", "hml", "prd"]:
            raise ValueError("ENVIRONMENT must be one of: local, dev, hml, prd")
        return v

    def is_local(self):
        return self.ENVIRONMENT == "local"

    def is_dev(self):
        return self.ENVIRONMENT == "dev"

    def is_hml(self):
        return self.ENVIRONMENT == "hml"

    def is_prd(self):
        return self.ENVIRONMENT == "prd"


class DatabaseSettings(Settings):
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_READ_ONLY_HOST: str = Field(default=None, env="DB_READ_ONLY_HOST")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_PORT: str = Field(..., env="DB_PORT")

    __BASE_TEMPLATE: str = "://{0}:{1}@{2}:{3}/{4}"
    __POSTGRES_ASYNC_TEMPLATE: str = "postgresql+asyncpg" + __BASE_TEMPLATE
    __POSTGRES_SYNC_TEMPLATE: str = "postgresql" + __BASE_TEMPLATE
    __MYSQL_SYNC_TEMPLATE: str = "mysql" + __BASE_TEMPLATE

    def __format_connection(self, template: str, read_only: bool) -> str:
        return template.format(
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_READ_ONLY_HOST if read_only else self.DB_HOST,
            self.DB_PORT,
            self.DB_NAME,
        )

    def get_mysql_db_url(self, read_only: bool = False) -> str:
        return self.__format_connection(self.__MYSQL_SYNC_TEMPLATE, read_only=read_only)

    def get_postgres_async_db_url(self, read_only: bool = False) -> str:
        return self.__format_connection(self.__POSTGRES_ASYNC_TEMPLATE, read_only=read_only)

    def get_postgres_sync_db_url(self, read_only: bool = False) -> str:
        return self.__format_connection(self.__POSTGRES_SYNC_TEMPLATE, read_only=read_only)

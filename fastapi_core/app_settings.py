from pydantic import BaseSettings, Field, validator


class AppSettings(BaseSettings):
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


class DatabaseSettings(BaseSettings):
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_READ_ONLY_HOST: str = Field(default=None, env="DB_READ_ONLY_HOST")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_PORT: str = Field(..., env="DB_PORT")

    def get_mysql_db_url(self):
        return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_postgres_sync_db_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

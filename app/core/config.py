from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = Field(..., alias="POSTGRES_HOST")
    db_port: str = Field(..., alias="POSTGRES_PORT")
    db_user: str = Field(..., alias="POSTGRES_USER")
    db_password: str = Field(..., alias="POSTGRES_PASSWORD")
    db_name: str = Field(..., alias="POSTGRES_DB")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        allow_population_by_field_name = True
        validate_by_name = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

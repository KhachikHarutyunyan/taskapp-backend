from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings

load_dotenv(override=False)


class Settings(BaseSettings):
    # MAIN
    APP_NAME: str
    API_VERSION: str
    SECRET_KEY: str
    EXAMPLE_URL: str
    TESTING: bool

    # AUTH
    JWT_ACCESS_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ACCESS_EXPIRE: int
    JWT_REFRESH_EXPIRE: int

    # REDIS
    REDIS_URL: str
    REDIS_PASSWORD: str
    REDIS_HOST: str

    # DB
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    TEST_DB: str

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def TEST_DB_URI(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_DB}"


settings = Settings()
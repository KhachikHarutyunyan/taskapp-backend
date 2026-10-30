from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
    def REDIS_URL(self) -> str:
        password = quote_plus(self.REDIS_PASSWORD)
        return f"redis://:{password}@{self.REDIS_HOST}:6379/0"

    @computed_field
    @property
    def TEST_DB_URI(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_DB}"


settings = Settings()

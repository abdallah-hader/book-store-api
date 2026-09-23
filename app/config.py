"""App settings, read from the environment and the .env file."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    app_name: str = "Book Store API"
    debug: bool = False
    database_url: str = "sqlite:///./bookstore.db"
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


# pydantic-settings fills secret_key from .env at runtime, which mypy cannot see.
settings = Settings()  # type: ignore[call-arg]

import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    MariaDBDsn,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file = ".env",
        env_file_encoding='utf-8',
        env_ignore_empty = False,
        arbitrary_types_allowed = True
    )
    API_V1_STR: str
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str
    SQLALCHEMY_DATABASE_URI: str
    SENTRY_DSN: str
    DB_SERVER: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DB: str
    DOMAIN: str
    FRONTEND_HOST: str
    ENVIRONMENT: str
    PROJECT_NAME: str
    STACK_NAME: str
    BACKEND_CORS_ORIGINS: str
    SECRET_KEY: str
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    SMTP_HOST: str
    SMTP_TLS: str
    SMTP_SSL: str
    SMTP_PORT: str
    DOCKER_IMAGE_BACKEND: str
    DOCKER_IMAGE_FRONTEND: str


settings = Settings()

print("---------------------")
print(str(settings.SQLALCHEMY_DATABASE_URI))
print("---------------------")
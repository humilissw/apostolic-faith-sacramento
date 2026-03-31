from typing import Any

from pydantic import (
    MariaDBDsn,
    MySQLDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    EMAIL_TEST_USER: str
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str
    # SQLALCHEMY_DATABASE_URI: str
    SENTRY_DSN: str
    DB_SERVER: str
    DB_PORT: int
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    emails_enabled: bool = False
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        return MySQLDsn.build(
    # def SQLALCHEMY_DATABASE_URI(self) -> MariaDBDsn:
    #     return MariaDBDsn.build(
            # scheme="mariadb+mariadbconnector",
            scheme="mysql+asyncmy",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_SERVER,
            port=self.DB_PORT,
            path=self.DB_DB,
        )



settings = Settings()

print("---------------------")
print(str(settings.SQLALCHEMY_DATABASE_URI))
print("---------------------")
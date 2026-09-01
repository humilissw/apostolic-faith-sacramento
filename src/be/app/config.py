from typing import Any
from urllib.parse import quote_plus

from pydantic import (
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
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=False,
        arbitrary_types_allowed=True,
    )
    API_V1_STR: str = "/api/v1"
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
    PROJECT_DESCRIPTION: str = "Sample API"
    VERSION: str = "1.0.0"
    STACK_NAME: str
    BACKEND_CORS_ORIGINS: str
    SECRET_KEY: str
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    SMTP_HOST: str
    SMTP_TLS: str
    SMTP_SSL: str
    SMTP_PORT: str
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    DOCKER_IMAGE_BACKEND: str
    DOCKER_IMAGE_FRONTEND: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1
    emails_enabled: bool = False
    cert_file: str
    cert_key: str
    rsa_pub_key: str
    rsa_private_key: str
    # OAuth 2.0 settings
    JWT_ISSUER: str = "apostolic-faith-sacramento"
    JWT_AUDIENCE: str
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    # Auth cookie settings
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = True
    COOKIE_DOMAIN: str = ""
    COOKIE_PATH: str = "/"
    COOKIE_SAMESITE: str = "none"
    # Stripe payment settings
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CURRENCY: str = "usd"
    # Third-party integration encryption
    INTEGRATION_ENCRYPTION_KEY: str = ""
    DEPLOY_QA_HOST: str = ""
    # Dev convenience: run `alembic upgrade head` on app startup (serialized across workers)
    RUN_MIGRATIONS_ON_STARTUP: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        # Percent-encode credentials: docker --env-file keeps inline comments,
        # so DB_PASSWORD may contain '#'/'@' etc. that break URL parsing.
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return MySQLDsn(
            f"mysql+pymysql://{user}:{password}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_ASYNC_DATABASE_URI(self) -> MySQLDsn:
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return MySQLDsn(
            f"mysql+asyncmy://{user}:{password}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DB}"
        )


settings = Settings()

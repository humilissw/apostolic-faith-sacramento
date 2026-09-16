"""Configuration for the AFC email microservice."""

import os
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_files() -> tuple[str, ...]:
    """Environment-specific .env files, later entries win.

    ``ENVIRONMENT`` (real env var) selects the overlay file:
    - local/development/dev -> .env.local
    - production/prod       -> .env.prod
    Those overlays are git-ignored; .env.example documents every key and is
    the container default. A plain ``.env`` (if present) always applies too.
    """
    env = os.getenv("ENVIRONMENT", "").strip().lower()
    overlay = {
        "local": ".env.local",
        "development": ".env.local",
        "dev": ".env.local",
        "production": ".env.prod",
        "prod": ".env.prod",
    }.get(env)
    files = [".env"]
    if overlay:
        files.append(overlay)
    return tuple(f for f in files if Path(__file__).resolve().parent.parent / f)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_resolve_env_files(),
        env_file_encoding="utf-8",
        env_ignore_empty=False,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Apostolic Faith Sacramento"
    ENVIRONMENT: str = "local"
    VERSION: str = "1.0.0"

    # ── SMTP delivery ──────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: str = "25"
    SMTP_TLS: str = "False"
    SMTP_SSL: str = "False"
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "no-reply@example.com"
    EMAILS_FROM_NAME: str = "Apostolic Faith Sacramento"

    # ── Frontend (reset links embedded in emails) ──────────────────────
    FRONTEND_HOST: str = "https://localhost:3000"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # ── Auth: RS256 JWTs issued by src/be/, verified with its public key.
    # Sending email requires the ``api:email`` scope in the token.
    RSA_PUB_KEY: str = "security_keys/public_key.pem"
    JWT_ISSUER: str = ""
    JWT_AUDIENCE: str = ""
    EMAIL_REQUIRED_SCOPE: str = "api:email"
    # Shared secret for trusted service-to-service calls (e.g. the backend's
    # unauthenticated password-recovery flow). Empty disables the fallback.
    SERVICE_API_KEY: str = ""

    # ── Shared application database (read-only access to ``users``).
    # Same MySQL instance as src/be/ until user management is extracted
    # into its own microservice.
    DB_SERVER: str = ""
    DB_PORT: str = "3306"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_DB: str = ""

    # ── Email-service-owned database (delivery tracking). Self-contained:
    # delivery history never lives in the shared application database.
    TRACKING_DB_URL: str = "sqlite:///data/email_delivery.db"

    @staticmethod
    def _as_bool(value: str) -> bool:
        """Parse env-style boolean strings ("False"/"0"/"" are disabled)."""
        return str(value).strip().lower() in {"1", "true", "yes", "on", "t"}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def smtp_configured(self) -> bool:
        """SMTP delivery is available once a host (or user) is configured."""
        return bool(self.SMTP_HOST.strip() or self.SMTP_USER.strip())

    @computed_field  # type: ignore[prop-decorator]
    @property
    def smtp_use_tls(self) -> bool:
        # SMTP_TLS/SMTP_SSL are plain strings from the environment; a raw
        # truthiness check would make "False" enable TLS. Parse them instead.
        return self._as_bool(self.SMTP_TLS) and not self._as_bool(self.SMTP_SSL)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def smtp_use_ssl(self) -> bool:
        return self._as_bool(self.SMTP_SSL)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def USERS_DB_URL(self) -> str:
        """Sync SQLAlchemy URL for the shared application database."""
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{user}:{password}@{self.DB_SERVER}:" f"{self.DB_PORT}/{self.DB_DB}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def users_db_configured(self) -> bool:
        return bool(self.DB_SERVER.strip() and self.DB_DB.strip())


settings = Settings()

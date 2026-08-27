"""Service for integration management operations."""

import json
from urllib.parse import urlparse

from app.repositories.integration_repo import IntegrationConfigRepository
from app.services.integration_service import KNOWN_INTEGRATIONS, IntegrationService


# SSRF protection: allowed schemes and blocked host patterns
ALLOWED_URL_SCHEMES = {"http", "https"}
BLOCKED_HOST_PATTERNS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "0:0:0:0:0:0:0:1",
    "::1",
    "metadata.google.internal",  # GCP metadata
    "169.254.169.254",  # AWS metadata
    "100.169.in-addr.arpa",  # AWS metadata reverse
]


class IntegrationManagementService:
    """Handles business logic for integration management operations."""

    def __init__(self, session):
        self.session = session
        self.service = IntegrationService(IntegrationConfigRepository(session))

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        """Get all integrations."""
        return await self.service.get_all(skip, limit)  # type: ignore[no-any-return]

    async def get_by_id(self, integration_id: str):
        """Get integration by ID."""
        return await self.service.get_by_id(integration_id)  # type: ignore[no-any-return]

    async def get_by_type(self, type_id: str):
        """Get integration by type."""
        return await self.service.get_by_type(type_id)  # type: ignore[no-any-return]

    async def create(
        self,
        type_id: str,
        display_name: str | None = None,
        icon: str | None = None,
        enabled: bool = False,
        config_json: str | None = None,
        credentials: dict[str, str] | None = None,
    ):
        """Create a new integration."""
        # Use KNOWN_INTEGRATIONS defaults if not provided
        meta = KNOWN_INTEGRATIONS.get(type_id, {})
        display_name = display_name or meta.get("display_name", type_id)
        icon = icon or meta.get("icon", "Plug")

        return await self.service.create(
            type=type_id,
            display_name=display_name,
            icon=icon,
            enabled=enabled,
            config_json=config_json,
            credentials=credentials or {},
        )

    async def update(self, integration, update_data: dict):
        """Update an integration."""
        return await self.service.update(integration, update_data)

    async def update_credentials(self, integration, credentials: dict):
        """Update only the credentials for an integration."""
        return await self.service.update_credentials(integration, credentials)

    async def delete(self, integration):
        """Delete an integration."""
        return await self.service.delete(integration)

    async def get_credentials(self, integration):
        """Get credentials for an integration (masked)."""
        return await self.service.get_credentials(integration)

    async def test_connection(
        self, type_id: str, credentials: dict | None = None, config_json: str | None = None
    ) -> dict:
        """Test connection for an integration type."""
        return await self.service.test_connection(  # type: ignore[no-any-return]
            type_id, credentials, config_json
        )

    async def sync_status(self, integration, status: str):
        """Manually update the connection status of an integration."""
        return await self.service.sync_status(integration, status)

    def mask_credentials(self, creds: dict[str, str] | None) -> dict[str, str]:
        """Mask sensitive credential values."""
        if not creds:
            return {}
        return {
            field: f"****{value[-4:]}" if len(value) > 4 else "****"
            for field, value in creds.items()
        }

    def is_url_safe(self, url: str) -> bool:
        """Validate that a URL is safe to connect to (SSRF protection)."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ALLOWED_URL_SCHEMES:
                return False
            host = parsed.hostname or ""
            for pattern in BLOCKED_HOST_PATTERNS:
                if pattern in host.lower():
                    return False
            return True
        except Exception:
            return False

    def parse_config_json(self, config_json: str | None) -> dict | None:
        """Parse config JSON string to dictionary."""
        if not config_json:
            return None
        try:
            return json.loads(config_json)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            raise ValueError("Invalid config_json")

    def validate_config_urls(self, config: dict) -> None:
        """Validate URLs in config against SSRF protection."""
        if not isinstance(config, dict):
            return
        for key, value in config.items():
            if isinstance(value, str) and ("url" in key.lower() or "endpoint" in key.lower()):
                if not self.is_url_safe(value):
                    raise ValueError(f"SSRF protection: URL for '{key}' is not allowed")

    async def create_pre_seeded_integrations(self) -> list:
        """Create placeholder entries for all known integration types."""
        created = []
        for type_id, meta in KNOWN_INTEGRATIONS.items():
            existing = await self.service.get_by_type(type_id)  # type: ignore[attr-defined]
            if not existing:
                created.append(
                    await self.service.create(  # type: ignore[misc]
                        type=type_id,
                        display_name=meta["display_name"],
                        icon=meta["icon"],
                        enabled=False,
                        config_json=None,
                        credentials={},
                    )
                )
        return created

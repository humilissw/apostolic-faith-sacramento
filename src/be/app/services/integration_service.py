"""Third-party integration service with encrypted credential storage and extensible handlers."""

import base64
import json
from typing import Any, Callable, Protocol

from cryptography.fernet import Fernet

from app.config import settings
from app.models import IntegrationConfig
from app.repositories.integration_repo import IntegrationConfigRepository

# Credential schemas: each type maps to its expected credential field names
CREDENTIAL_SCHEMAS: dict[str, list[str]] = {
    "stripe": ["secret_key", "public_key", "webhook_secret"],
    "twilio": ["account_sid", "auth_token"],
    "sendgrid": ["api_key"],
    "youtube": ["api_key"],
    "facebook": ["app_id", "app_secret"],
    "spotify": ["client_id", "client_secret"],
}

# Known integration types with display metadata
KNOWN_INTEGRATIONS: dict[str, dict[str, str]] = {
    "stripe": {"display_name": "Stripe Payments", "icon": "CreditCard"},
    "twilio": {"display_name": "Twilio SMS", "icon": "MessageSquare"},
    "sendgrid": {"display_name": "SendGrid Email", "icon": "Mail"},
    "youtube": {"display_name": "YouTube", "icon": "Youtube"},
    "facebook": {"display_name": "Facebook", "icon": "Facebook"},
    "spotify": {"display_name": "Spotify Music", "icon": "Music"},
}

# Connection handler registry
_CONNECTION_HANDLERS: dict[str, Callable] = {}


def register_connection_handler(type_name: str):
    """Decorator to register a connection test handler for an integration type."""

    def decorator(fn):
        _CONNECTION_HANDLERS[type_name] = fn
        return fn

    return decorator


class ConnectionHandler(Protocol):
    async def __call__(
        self, credentials: dict[str, str], config: dict | None
    ) -> dict[str, Any]: ...


class EncryptionHelper:
    @staticmethod
    def _get_fernet() -> Fernet:
        key = settings.INTEGRATION_ENCRYPTION_KEY
        if not key:
            raise ValueError("INTEGRATION_ENCRYPTION_KEY not configured")
        key_bytes = key.encode() if isinstance(key, str) else key
        if len(key_bytes) == 32:
            return Fernet(key_bytes)
        import hashlib

        derived = hashlib.sha256(key_bytes).digest()
        return Fernet(base64.urlsafe_b64encode(derived))

    @staticmethod
    def encrypt(plaintext: str) -> tuple[str, str]:
        fernet = EncryptionHelper._get_fernet()
        token = fernet.encrypt(plaintext.encode())
        iv = token[:16].hex()
        return iv, base64.urlsafe_b64encode(token).decode()

    @staticmethod
    def decrypt(iv: str, encrypted_blob: str) -> str:
        fernet = EncryptionHelper._get_fernet()
        token_bytes = base64.urlsafe_b64decode(encrypted_blob)
        return fernet.decrypt(token_bytes).decode()  # type: ignore[no-any-return]


class IntegrationService:
    def __init__(self, repository: IntegrationConfigRepository):
        self.repo = repository

    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[IntegrationConfig], int]:
        return await self.repo.get_all(skip, limit)

    async def get_by_id(self, id: str) -> IntegrationConfig | None:
        return await self.repo.get_by_id(id)

    async def get_by_type(self, type: str) -> IntegrationConfig | None:
        return await self.repo.get_by_type(type)

    async def create(
        self,
        type: str,
        display_name: str,
        icon: str,
        enabled: bool,
        config_json: str | None,
        credentials: dict[str, str],
    ) -> IntegrationConfig:
        data = {
            "type": type,
            "display_name": display_name,
            "icon": icon,
            "enabled": enabled,
            "config_json": config_json,
        }
        if credentials:
            iv, blob = EncryptionHelper.encrypt(json.dumps(credentials))
            data["cred_encrypted_iv"] = iv
            data["cred_encrypted_blob"] = blob
            data["status"] = "disconnected"

        return await self.repo.create(data)

    async def update(self, db_item: IntegrationConfig, data: dict) -> IntegrationConfig:
        return await self.repo.update(db_item, data)

    async def update_credentials(
        self, db_item: IntegrationConfig, credentials: dict[str, str]
    ) -> IntegrationConfig:
        iv, blob = EncryptionHelper.encrypt(json.dumps(credentials))
        db_item.cred_encrypted_iv = iv
        db_item.cred_encrypted_blob = blob
        db_item.updated_on = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )
        self.repo.session.add(db_item)
        await self.repo.session.commit()
        await self.repo.session.refresh(db_item)
        return db_item

    async def delete(self, db_item: IntegrationConfig) -> None:
        await self.repo.delete(db_item)

    async def get_credentials(self, integration: IntegrationConfig) -> dict[str, str] | None:
        if not integration.cred_encrypted_blob or not integration.cred_encrypted_iv:
            return None
        plaintext = EncryptionHelper.decrypt(
            integration.cred_encrypted_iv,
            integration.cred_encrypted_blob,
        )
        result: dict[str, str] = json.loads(plaintext)  # type: ignore[assignment]
        return result

    async def test_connection(
        self, type: str, credentials: dict[str, str], config: dict | None = None
    ) -> dict[str, Any]:
        handler = _CONNECTION_HANDLERS.get(type)
        if not handler:
            return {"success": False, "status": "error", "message": f"No handler for type '{type}'"}
        result = await handler(credentials, config)
        return result  # type: ignore[no-any-return]

    async def sync_status(self, integration: IntegrationConfig, status: str) -> IntegrationConfig:
        integration.status = status
        integration.last_synced_at = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )
        self.repo.session.add(integration)
        await self.repo.session.commit()
        await self.repo.session.refresh(integration)
        return integration

    @staticmethod
    async def pre_seed() -> list[IntegrationConfig]:
        """Create placeholder entries for known integration types if they don't exist."""

        # We need access to the session — this is a static method that the route calls
        # with the session passed in. We'll use the repository pattern instead.
        return []  # placeholder, actual pre-seed done via route


# --- Built-in connection handlers ---


@register_connection_handler("stripe")
async def _test_stripe(credentials: dict[str, str], config: dict | None) -> dict[str, Any]:
    import stripe

    secret_key = credentials.get("secret_key", "")
    if not secret_key:
        return {"success": False, "status": "error", "message": "Missing secret_key"}
    stripe.api_key = secret_key
    try:
        stripe.BalanceTransaction.list(limit=1)
        return {"success": True, "status": "connected", "message": "Stripe API reachable"}
    except stripe.error.StripeError as e:  # type: ignore[attr-defined]
        return {
            "success": False,
            "status": "error",
            "message": f"Stripe authentication failed: {str(e)}",
        }


@register_connection_handler("twilio")
async def _test_twilio(credentials: dict[str, str], config: dict | None) -> dict[str, Any]:
    try:
        from twilio.rest import Client  # type: ignore[import-not-found]
    except ImportError:
        return {"success": False, "status": "error", "message": "twilio package not installed"}
    account_sid = credentials.get("account_sid", "")
    auth_token = credentials.get("auth_token", "")
    if not account_sid or not auth_token:
        return {"success": False, "status": "error", "message": "Missing account_sid or auth_token"}
    client = Client(account_sid, auth_token)
    try:
        await client.api.v2010.accounts(account_sid).fetch_async()
        return {"success": True, "status": "connected", "message": "Twilio API reachable"}
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"Twilio authentication failed: {str(e)}",
        }


@register_connection_handler("sendgrid")
async def _test_sendgrid(credentials: dict[str, str], config: dict | None) -> dict[str, Any]:
    api_key = credentials.get("api_key", "")
    if not api_key:
        return {"success": False, "status": "error", "message": "Missing api_key"}
    import httpx

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://api.sendgrid.com/v3/user/profile",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            if resp.status_code == 200:
                return {"success": True, "status": "connected", "message": "SendGrid API reachable"}
            return {
                "success": False,
                "status": "error",
                "message": f"SendGrid responded with {resp.status_code}",
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"SendGrid connection failed: {str(e)}",
            }


@register_connection_handler("youtube")
async def _test_youtube(credentials: dict[str, str], config: dict | None) -> dict[str, Any]:
    api_key = credentials.get("api_key", "")
    if not api_key:
        return {"success": False, "status": "error", "message": "Missing api_key"}
    import httpx

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={"part": "snippet", "mine": "true"},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            if resp.status_code == 200:
                return {"success": True, "status": "connected", "message": "YouTube API reachable"}
            return {
                "success": False,
                "status": "error",
                "message": f"YouTube responded with {resp.status_code}",
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"YouTube connection failed: {str(e)}",
            }


@register_connection_handler("facebook")
async def _test_facebook(credentials: dict[str, str], config: dict | None) -> dict[str, Any]:
    app_id = credentials.get("app_id", "")
    app_secret = credentials.get("app_secret", "")
    if not app_id or not app_secret:
        return {"success": False, "status": "error", "message": "Missing app_id or app_secret"}
    import httpx

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"https://graph.facebook.com/{app_id}",
                params={"fields": "id,name", "access_token": f"{app_id}|{app_secret}"},
                timeout=10.0,
            )
            if resp.status_code == 200:
                return {"success": True, "status": "connected", "message": "Facebook API reachable"}
            return {
                "success": False,
                "status": "error",
                "message": f"Facebook responded with {resp.status_code}",
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"Facebook connection failed: {str(e)}",
            }


@register_connection_handler("spotify")
async def _test_spotify(credentials: dict[str, str], config: dict | None) -> dict[str, Any]:
    client_id = credentials.get("client_id", "")
    client_secret = credentials.get("client_secret", "")
    if not client_id or not client_secret:
        return {
            "success": False,
            "status": "error",
            "message": "Missing client_id or client_secret",
        }
    import httpx

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                timeout=10.0,
            )
            if resp.status_code == 200:
                return {"success": True, "status": "connected", "message": "Spotify API reachable"}
            return {
                "success": False,
                "status": "error",
                "message": f"Spotify responded with {resp.status_code}",
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"Spotify connection failed: {str(e)}",
            }

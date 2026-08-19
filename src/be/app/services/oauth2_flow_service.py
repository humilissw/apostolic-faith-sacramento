"""Service for OAuth2 flow business logic."""

from datetime import datetime, timedelta, timezone
import secrets

from app.config import settings
from app.core.scopes import Scope
from app.core.security import (
    create_access_token_with_claims,
    create_refresh_token_with_expiry,
    generate_code_challenge,
    verify_password,
)
from app.models import (
    AuthorizationCode,
    ClientCredentials,
    RefreshToken,
    User,
)


class OAuth2FlowService:
    """Handles business logic for all OAuth2 flows."""

    def __init__(self, session):
        self.session = session

    # ---- Password Grant ----

    async def authenticate_user(self, email: str, password: str) -> tuple[User | None, str | None]:
        """Authenticate a user by email/password. Returns (user, error_message)."""
        from app.repositories.user_repo import UserRepository

        user_repo = UserRepository(session=self.session)
        user = await user_repo.get_by_email(email)
        if user is None:
            return None, "Incorrect email or password"
        if not verify_password(password, user.hashed_password):
            return None, "Incorrect email or password"
        if not user.is_active:
            return None, "Inactive user"
        return user, None

    # ---- Client Credentials Flow ----

    async def authenticate_client(
        self, client_id: str, client_secret: str
    ) -> tuple[ClientCredentials | None, list[str]]:
        """Authenticate an OAuth2 client. Returns (client, scopes)."""
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(ClientCredentials)
            .where(
                ClientCredentials.client_id == client_id,  # type: ignore[arg-type]
                ClientCredentials.is_active.is_(True),  # type: ignore[attr-defined, arg-type]
            )
        )
        client = result.scalar_one_or_none()
        if client is None:
            return None, []
        if not verify_password(client_secret, client.client_secret_hash):
            return None, []
        token_scopes = client.scopes.split(",") if client.scopes else []
        return client, token_scopes

    async def create_client_tokens(
        self, client_id: str, token_scopes: list[str]
    ) -> tuple[str, int, str, datetime]:
        """Create access and refresh tokens for a client credentials flow."""
        access_token, access_expires = self._create_access_token_for_client(client_id, token_scopes)
        refresh_token_str, refresh_expires = self._create_refresh_token()

        # Store refresh token keyed on client_id
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(RefreshToken)
            .where(RefreshToken.user_id == "client:" + str(client_id))  # type: ignore[arg-type]
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.token = refresh_token_str
            existing.expires_at = refresh_expires
            existing.revoked = False
        else:
            db_refresh = RefreshToken(
                user_id="client:" + client_id,
                token=refresh_token_str,
                expires_at=refresh_expires,
            )
            self.session.add(db_refresh)
        await self.session.commit()

        return access_token, access_expires, refresh_token_str, refresh_expires

    # ---- Authorization Code Flow ----

    async def create_authorization_code(
        self, client_id: str, code_challenge: str, redirect_uri: str
    ) -> tuple[str | None, str]:
        """Create an authorization code. Returns (code_or_none, error_message)."""
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(ClientCredentials)
            .where(
                ClientCredentials.client_id == client_id,  # type: ignore[arg-type]
                ClientCredentials.is_active.is_(True),  # type: ignore[attr-defined, arg-type]
            )
        )
        client = result.scalar_one_or_none()
        if client is None:
            return None, "Invalid client credentials"

        auth_code = secrets.token_urlsafe(32)
        db_code = AuthorizationCode(
            code=auth_code,
            client_id=client_id,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        self.session.add(db_code)
        await self.session.commit()
        return auth_code, ""

    async def exchange_authorization_code(
        self,
        client_id: str,
        code: str,
        code_verifier: str,
    ) -> tuple[str | None, int | None, str | None]:
        """Exchange an authorization code for tokens."""
        # Find stored authorization code
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(AuthorizationCode)
            .where(AuthorizationCode.code == code)  # type: ignore[arg-type]
        )
        stored = result.scalar_one_or_none()

        if stored is None:
            return None, None, "Invalid authorization code"
        if stored.used:
            return None, None, "Authorization code already used"
        expires = stored.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return None, None, "Authorization code has expired"

        # Verify client_id matches
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(ClientCredentials)
            .where(
                ClientCredentials.client_id == client_id,  # type: ignore[arg-type]
                ClientCredentials.is_active.is_(True),  # type: ignore[attr-defined, arg-type]
            )
        )
        client = result.scalar_one_or_none()

        if client is None:
            return None, None, "Invalid client credentials"

        if stored.client_id != client_id:
            return None, None, "Authorization code client_id mismatch"

        # Verify PKCE code_verifier
        expected_challenge = generate_code_challenge(code_verifier)
        if stored.code_challenge != expected_challenge:
            return None, None, "PKCE code_challenge mismatch"

        # Issue tokens using client scopes
        scopes_raw = client.scopes  # type: ignore[attr-defined]
        token_scopes = scopes_raw.split(",") if scopes_raw else ["client"]

        access_token, access_expires = self._create_access_token_for_client(client_id, token_scopes)
        refresh_token_str, refresh_expires = self._create_refresh_token()

        # Mark code as used
        stored.used = True
        await self.session.commit()

        # Store refresh token keyed on client_id
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(RefreshToken)
            .where(RefreshToken.user_id == "client:" + client_id)  # type: ignore[arg-type]
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.token = refresh_token_str
            existing.expires_at = refresh_expires
            existing.revoked = False
        else:
            db_refresh = RefreshToken(
                user_id="client:" + client_id,
                token=refresh_token_str,
                expires_at=refresh_expires,
            )
            self.session.add(db_refresh)
        await self.session.commit()

        return (
            access_token,
            int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
            None,
        )

    # ---- Implicit Grant Flow ----

    async def issue_implicit_token(
        self, client_id: str, code_verifier: str
    ) -> tuple[str | None, int | None, str]:
        """Issue an implicit grant token. Returns (access_token, expires_in_sec, error)."""
        result = await self.session.execute(
            __import__("sqlalchemy")
            .select(ClientCredentials)
            .where(
                ClientCredentials.client_id == client_id,  # type: ignore[arg-type]
                ClientCredentials.is_active.is_(True),  # type: ignore[attr-defined, arg-type]
            )
        )
        client = result.scalar_one_or_none()

        if client is None:
            return None, None, "Invalid client credentials"

        token_scopes = ["spa:all"]
        if client.scopes:
            client_scopes = client.scopes.split(",")
            known = {s.value for s in Scope}
            token_scopes = [s for s in client_scopes if s in known] or ["spa:all"]

        access_token, access_expires = self._create_access_token_for_client(client_id, token_scopes)
        return access_token, access_expires, ""

    # ---- Helpers ----

    def _create_access_token_for_client(self, subject: str, scopes: list[str]) -> tuple[str, int]:
        """Create an access token for client-credentials/implicit/auth-code flows."""
        return create_access_token_with_claims(
            subject,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            scopes=scopes,
        )

    def _create_refresh_token(self) -> tuple[str, datetime]:
        """Create a refresh token with expiry."""
        return create_refresh_token_with_expiry(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

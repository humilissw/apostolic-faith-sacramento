"""Service for Google OAuth authentication business logic."""

import asyncio
from datetime import timedelta
from typing import Any, cast

from fastapi import HTTPException, status

from app.config import settings
from app.core import security
from app.core.scopes import Scope
from app.models import Message, RefreshToken, UserCreate
from app.repositories.user_repo import UserRepository
from app.repositories.user_scope_repo import UserScopeRepository


class GoogleAuthService:
    """Handles business logic for Google OAuth authentication flows."""

    def __init__(self, session):
        self.session = session

    async def build_oauth(self):
        """Build an OAuth instance with Google credentials from settings.

        Raises HTTPException if Google OAuth is not configured.
        """
        from authlib.integrations.starlette_client import OAuth

        if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "dummy":
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=(
                    "Google OAuth is not configured. "
                    "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
                ),
            )
        oauth = OAuth()
        oauth.register(
            name="google",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile",
                "access_type": "offline",
                "prompt": "consent",
            },
        )
        return oauth

    async def generate_pkce_pair(self) -> tuple[str, str]:
        """Generate a PKCE code_verifier and code_challenge pair."""
        code_verifier = security.generate_code_verifier()
        code_challenge = security.generate_code_challenge(code_verifier)
        return code_verifier, code_challenge

    async def verify_google_id_token(self, id_token: str) -> dict:
        """Verify a Google ID token and return the payload.

        Raises HTTPException if verification fails or email is not verified.
        """
        from google.auth import jwt as google_jwt

        credentials, payload = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: google_jwt.verify_id_token(  # type: ignore[no-any-return]
                id_token, settings.GOOGLE_CLIENT_ID
            ),
        )

        email = payload.get("email")
        if not email or not payload.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google email not verified",
            )
        return cast(dict[Any, Any], payload)

    async def get_or_create_user_from_google(self, email: str, full_name: str):
        """Find or create a user from Google OAuth data.

        Returns the User object. Raises HTTPException for inactive users.
        """
        repository = UserRepository(session=self.session)
        user = await repository.get_by_email(email=email)

        if user is None:
            # Don't set a password for Google OAuth users — they must claim their account
            # via email verification or password setup. Store with an unusable hash.
            from app.core.security import get_password_hash

            user_in = UserCreate(
                email=email,
                full_name=full_name,
                password=get_password_hash(security.generate_code_verifier()),  # Unusable hash
                is_active=False,  # Inactive until they claim account with a real password
                is_superuser=False,
            )
            from app.crud import create_user

            user = await create_user(session=self.session, user_create=user_in)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        return user

    async def resolve_user_scopes(self, user_id: str) -> list[str]:
        """Resolve scopes for a user based on their assigned roles."""
        scope_repo = UserScopeRepository(self.session)
        db_scopes = await scope_repo.get_scopes(user_id)
        if "superuser" in db_scopes:
            return [s.value for s in Scope]
        elif db_scopes:
            return db_scopes
        return []

    async def create_tokens_for_user(self, user) -> tuple[str, str]:
        """Create access and refresh tokens for a user.

        Returns (access_token, refresh_token). Stores the refresh token in DB.
        """
        user_scopes = await self.resolve_user_scopes(user.id)

        access_token, _ = security.create_access_token_with_claims(
            user.email,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            scopes=user_scopes,
        )
        refresh_token_str, refresh_expires = security.create_refresh_token_with_expiry(
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        db_refresh = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=refresh_expires,
        )
        self.session.add(db_refresh)
        await self.session.commit()

        return access_token, refresh_token_str

    async def google_logout(self, current_user) -> Message:
        """Revoke all refresh tokens for a user."""
        from sqlalchemy import update as sa_update

        await self.session.execute(
            sa_update(RefreshToken)
            .where(RefreshToken.user_id == current_user.id)  # type: ignore[arg-type]
            .where(RefreshToken.revoked.is_(False))  # type: ignore[attr-defined, arg-type]
            .values(revoked=True)
        )
        await self.session.commit()
        return Message(message="Logged out via Google")

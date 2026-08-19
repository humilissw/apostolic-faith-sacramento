"""
Authentication token service for managing JWT token lifecycle operations.

Handles:
- Token generation (access + refresh)
- Token validation and decoding
- Refresh token storage and rotation
- Scope resolution from database
- Cookie configuration

This service owns the business logic for authentication tokens so that
route handlers only deal with HTTP concerns (requests, responses, cookies).
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Request, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.scopes import Scope
from app.core.security import (
    create_access_token_with_claims,
    create_refresh_token_with_expiry,
)
from app.models import RefreshToken, User


class AuthTokenService:
    """Manages JWT access/refresh token lifecycle and cookie handling."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------ #
    #  Scope resolution                                                    #
    # ------------------------------------------------------------------ #

    async def resolve_user_scopes(self, user_id: str) -> list[str]:
        """Return all effective scopes for a user (superuser gets all)."""
        from app.repositories.user_scope_repo import UserScopeRepository

        repo = UserScopeRepository(self.session)
        assigned = await repo.get_scopes(user_id)
        if "superuser" in assigned:
            return [s.value for s in Scope]
        return list(assigned) if assigned else []

    # ------------------------------------------------------------------ #
    #  Token generation                                                    #
    # ------------------------------------------------------------------ #

    async def create_tokens_for_user(self, user: User) -> dict[str, Any]:
        """Create access + refresh tokens for a user and persist the refresh token.

        Returns a dict with keys: access_token, refresh_token, access_expires,
        refresh_expires, scopes.
        """
        scopes = await self.resolve_user_scopes(user.id)

        access_token, access_expires = create_access_token_with_claims(
            user.email,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            scopes=scopes,
        )
        refresh_token, refresh_expires = create_refresh_token_with_expiry(
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        # Persist refresh token in DB
        db_refresh = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_expires,
        )
        self.session.add(db_refresh)
        await self.session.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_expires": access_expires,
            "refresh_expires": int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
            "scopes": scopes,
        }

    # ------------------------------------------------------------------ #
    #  Token refresh                                                       #
    # ------------------------------------------------------------------ #

    async def refresh_access_token(self, raw_refresh_token: str) -> dict[str, Any]:
        """Validate and rotate a refresh token, returning new tokens.

        Raises HTTPException on invalid/expired/revoked tokens.
        """
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token == raw_refresh_token,  # type: ignore[arg-type]
                RefreshToken.revoked.is_(False),  # type: ignore[attr-defined]
            )
        )
        stored = result.scalar_one_or_none()

        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        expires = stored.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            stored.revoked = True
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        user = await self.session.get(User, stored.user_id)
        if user is None or not user.is_active:
            stored.revoked = True
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Rotate: revoke old, issue new
        stored.revoked = True
        await self.session.commit()

        scopes = await self.resolve_user_scopes(user.id)
        new_access_token, new_expires = create_access_token_with_claims(
            user.email,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            scopes=scopes,
        )
        new_refresh_token, new_refresh_expires = create_refresh_token_with_expiry(
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        new_stored = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=new_refresh_expires,
        )
        self.session.add(new_stored)
        await self.session.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "access_expires": new_expires,
            "refresh_expires": int(
                (new_refresh_expires - datetime.now(timezone.utc)).total_seconds()
            ),
            "scopes": scopes,
        }

    # ------------------------------------------------------------------ #
    #  Cookie helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def cookie_kwargs(request: Request) -> dict[str, Any]:
        """Compute cookie kwargs that work across HTTP and HTTPS."""
        scheme = request.url.scheme
        secure = scheme == "https"
        samesite = "none" if secure else "lax"
        return {
            "httponly": True,
            "secure": secure,
            "samesite": samesite,
            "path": settings.COOKIE_PATH,
            "domain": settings.COOKIE_DOMAIN,
        }

    @staticmethod
    def attach_auth_cookies(
        response: Response,
        access_token: str,
        refresh_token: str,
        request: Request | None = None,
    ) -> None:
        """Set httpOnly cookies for both tokens on the response."""
        kwargs = (
            AuthTokenService.cookie_kwargs(request)
            if request
            else {
                "httponly": True,
                "secure": settings.COOKIE_SECURE,
                "samesite": "lax",
                "path": settings.COOKIE_PATH,
                "domain": settings.COOKIE_DOMAIN,
            }
        )
        access_expire_minutes = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expire_days = int(settings.REFRESH_TOKEN_EXPIRE_DAYS)

        response.set_cookie(
            key=settings.ACCESS_TOKEN_COOKIE_NAME,
            value=access_token,
            max_age=60 * access_expire_minutes,
            **kwargs,
        )
        response.set_cookie(
            key=settings.REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token,
            max_age=60 * 60 * 24 * refresh_expire_days,
            **kwargs,
        )

    @staticmethod
    def clear_auth_cookies(response: Response, request: Request) -> None:
        """Clear auth cookies by setting empty values with max-age=0."""
        kwargs = AuthTokenService.cookie_kwargs(request)
        response.set_cookie(key=settings.ACCESS_TOKEN_COOKIE_NAME, value="", max_age=0, **kwargs)
        response.set_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, value="", max_age=0, **kwargs)

    # ------------------------------------------------------------------ #
    #  Logout                                                              #
    # ------------------------------------------------------------------ #

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke every active refresh token for a user."""
        from sqlalchemy import update as sa_update

        await self.session.execute(
            sa_update(RefreshToken)
            .where(RefreshToken.user_id == user_id)  # type: ignore[arg-type]
            .where(RefreshToken.revoked.is_(False))  # type: ignore[attr-defined, arg-type]
            .values(revoked=True)
        )
        await self.session.commit()

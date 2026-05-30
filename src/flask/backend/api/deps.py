"""Flask dependency injection for authentication and database sessions."""

from typing import Annotated, Callable

import jwt
from flask import Request, g, request
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import settings
from backend.core import security
from backend.core.db import SyncSessionLocal
from backend.models import TokenPayload, User


def _decode_jwt(token: str) -> dict:
    """Decode and verify a JWT token, omitting None audience/issuer."""
    decode_kwargs: dict[str, str] = {
        "algorithms": [security.ALGORITHM],
    }
    aud = getattr(settings, "JWT_AUDIENCE", None)
    iss = getattr(settings, "JWT_ISSUER", None)
    if aud:
        decode_kwargs["audience"] = aud
    if iss:
        decode_kwargs["issuer"] = iss
    return dict(jwt.decode(token, security.PUBLIC_KEY, **decode_kwargs))


def get_db() -> Session:
    """Get sync database session from Flask app context."""
    if "db" not in g:
        g.db = SyncSessionLocal()
    return g.db


def cleanup_db(response):
    """Close DB session at app teardown."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_token_from_cookie(req: Request) -> str | None:
    """Extract access token from httpOnly cookie."""
    token = req.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    return str(token) if token else None


def get_current_user() -> User:
    """Validate JWT token and return current user (cookie or header)."""
    cookie_token = get_token_from_cookie(request)

    auth_header = request.headers.get("authorization", "")
    header_token = None
    if auth_header.startswith("Bearer "):
        header_token = auth_header[7:]

    token_to_use = cookie_token or header_token
    if not token_to_use:
        from flask import abort

        abort(403, "Could not validate credentials")

    try:
        payload = _decode_jwt(token_to_use)
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        from flask import abort

        abort(403, "Could not validate credentials")

    session = get_db()
    user = session.execute(select(User).where(User.email == token_data.sub)).scalar_one_or_none()
    if user is None:
        from flask import abort

        abort(404, "User not found")
    if not getattr(user, "is_active", True):
        from flask import abort

        abort(400, "Inactive user")
    return user


def get_current_active_superuser() -> User:
    """Validate token and check superuser scope."""
    user = get_current_user()
    token_data = _get_token_scopes()
    if "superuser" not in (token_data.scopes or []):
        from flask import abort

        abort(403, "The user doesn't have enough privileges")
    return user


CurrentUser = Annotated[User, "current user from JWT"]


def require_scope(required_scope: str) -> Callable:
    """Decorator that checks if user has required scope."""

    def decorator(fn):
        def wrapper(*args, **kwargs):
            get_current_user()
            token_data = _get_token_scopes()

            if "superuser" in token_data.scopes or "api:all" in token_data.scopes:
                return fn(*args, **kwargs)
            if required_scope not in token_data.scopes:
                from flask import jsonify

                return jsonify({"detail": f"Missing required scope: {required_scope}"}), 403
            return fn(*args, **kwargs)

        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator


def _get_token_scopes() -> TokenPayload:
    auth_header = request.headers.get("authorization", "")
    header_token = None
    if auth_header.startswith("Bearer "):
        header_token = auth_header[7:]
    cookie_token = get_token_from_cookie(request)
    token_to_use = cookie_token or header_token
    if not token_to_use:
        return TokenPayload(scopes=[])
    try:
        payload = jwt.decode(
            token_to_use,
            security.PUBLIC_KEY,
            algorithms=[security.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        return TokenPayload(**payload)
    except Exception:
        return TokenPayload(scopes=[])

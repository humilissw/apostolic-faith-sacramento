"""FastAPI auth dependencies for the email microservice."""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.core.security import decode_token, has_email_scope, is_superuser_token


@dataclass
class EmailCaller:
    """Authenticated identity of a send request."""

    subject: str
    via: str  # "jwt" | "api-key"
    is_superuser: bool = False


bearer_scheme = HTTPBearer(auto_error=False)


async def require_email_scope(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> EmailCaller:
    """Authorize a send request.

    Accepts either:
    - ``Authorization: Bearer <jwt>`` — an RS256 JWT issued by src/be/,
    verified with the backend's public key and required to carry the
    ``api:email`` scope (superuser tokens also qualify).
    - ``X-API-Key: <key>`` — the shared service API key for trusted
    server-to-server calls (e.g. unauthenticated password-recovery).

    The email service never issues or refreshes tokens; verification only.
    """
    api_key = request.headers.get("x-api-key")
    if api_key:
        if settings.SERVICE_API_KEY and hmac.compare_digest(
            api_key.encode("utf-8"), settings.SERVICE_API_KEY.encode("utf-8")
        ):
            return EmailCaller(subject="api-key", via="api-key", is_superuser=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide a Bearer token or X-API-Key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    superuser = is_superuser_token(payload)
    if not (has_email_scope(payload) or superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required scope: {settings.EMAIL_REQUIRED_SCOPE}",
        )

    return EmailCaller(subject=str(payload.get("sub", "")), via="jwt", is_superuser=superuser)


CallerDep = Annotated[EmailCaller, Depends(require_email_scope)]

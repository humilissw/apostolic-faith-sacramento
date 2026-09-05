from datetime import datetime, timezone
from typing import Annotated, Any

import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from app.config import settings
from app.core.db import get_db_session
from app.core.security import (
    generate_code_challenge,
    generate_code_verifier,
    verify_access_token,
    verify_password,
)
from app.models import (
    Message,
    NewPassword,
    PasswordRecoveryRequest,
    RefreshToken,
    RevokeTokenRequest,
    Token,
    TokenRefresh,
    TokenScopes,
    UpdateTokenResponse,
    User,
    UserPublic,
)
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.services.auth_token_service import AuthTokenService
from app.services.oauth2_flow_service import OAuth2FlowService

logger = logging.getLogger(__name__)


router = APIRouter(tags=["login"])


# --- Pydantic request/response models for OAuth2 flows ---


class AuthorizationCodeRequest(BaseModel):
    """Request to exchange an authorization code for tokens."""

    client_id: str
    code: str
    code_verifier: str
    redirect_uri: str = ""


class AuthorizationCodeChallenge(BaseModel):
    """Request to generate an authorization code (authorization step of auth code flow)."""

    client_id: str
    code_challenge: str
    redirect_uri: str = ""


class AuthorizationCodeResponse(BaseModel):
    """Response from authorization code generation."""

    access_token: str = Field(min_length=1)
    token_type: str = "code"
    expires_in: int = 600
    scope: str = ""


class ImplicitTokenRequest(BaseModel):
    """Request for implicit grant token."""

    client_id: str
    code_challenge: str
    code_verifier: str
    redirect_uri: str = ""


class ImplicitTokenResponse(BaseModel):
    """Response from implicit grant token endpoint."""

    access_token: str = Field(min_length=1)
    token_type: str = "bearer"
    expires_in: int
    scope: str = ""


# --------------------------------------------------------------------------- #
#  PKCE challenge                                                             #
# --------------------------------------------------------------------------- #


@router.post("/login/pkce-challenge")
async def pkce_challenge() -> dict:
    """Generate a PKCE code_verifier and code_challenge pair."""
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    return {
        "code_verifier": verifier,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }


# --------------------------------------------------------------------------- #
#  Password grant (email/password login)                                      #
# --------------------------------------------------------------------------- #


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    *,
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    """OAuth2 password grant — returns tokens in JSON body and httpOnly cookies."""
    from app.core.rate_limiter import (
        LOGIN_MAX_ATTEMPTS,
        LOGIN_WINDOW_SECONDS,
        check_rate_limit,
        get_client_ip,
        login_bucket_key,
        reset_rate_bucket,
        retry_after_seconds,
    )

    ip = get_client_ip(request)

    # Lockout check only: the bucket is consumed exclusively by *failed*
    # credential attempts below, and cleared on a successful login. This way
    # legitimate users logging in repeatedly are never rate-limited.
    key = login_bucket_key(ip)
    if not check_rate_limit(key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS, consume=False):
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after_seconds(key, LOGIN_WINDOW_SECONDS))},
        )

    def _record_failed_attempt() -> None:
        # Consume one slot for this failed attempt (brute-force protection).
        check_rate_limit(key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS)

    # Authenticate user via repository (separate from token lifecycle)
    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_email(form_data.username)
    if user is None:
        logger.warning(
            "Failed login attempt for non-existent email: %s | ip=%s", form_data.username, ip
        )
        _record_failed_attempt()
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning("Failed login attempt for email: %s | ip=%s", form_data.username, ip)
        _record_failed_attempt()
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        logger.info("Login attempt by inactive user: %s | ip=%s", form_data.username, ip)
        raise HTTPException(status_code=400, detail="Inactive user")

    # Successful credentials: clear any failed-attempt lockout for this IP.
    reset_rate_bucket(key)

    # Delegate token creation + cookie setting to service
    token_svc = AuthTokenService(session=session)
    tokens = await token_svc.create_tokens_for_user(user)
    AuthTokenService.attach_auth_cookies(
        response, tokens["access_token"], tokens["refresh_token"], request
    )

    logger.info("Successful login: %s | ip=%s", form_data.username, ip)

    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        access_token_expires=tokens["access_expires"],
        refresh_token_expires=tokens["refresh_expires"],
        scopes=tokens["scopes"],
    )


# --------------------------------------------------------------------------- #
#  Token refresh                                                              #
# --------------------------------------------------------------------------- #


@router.post("/login/refresh-token", response_model=UpdateTokenResponse)
async def refresh_token(
    body: TokenRefresh,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    response: Response = Response(),
) -> UpdateTokenResponse:
    """Exchange a valid refresh token for a new access token (single-use rotation).

    The refresh token may arrive in the JSON body (API clients) or in the
    httpOnly cookie (web app — it cannot read its own cookies).
    """
    refresh_token_value = body.refresh_token or request.cookies.get(
        settings.REFRESH_TOKEN_COOKIE_NAME, ""
    )
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_svc = AuthTokenService(session=session)
    tokens = await token_svc.refresh_access_token(refresh_token_value)

    AuthTokenService.attach_auth_cookies(
        response, tokens["access_token"], tokens["refresh_token"], request
    )

    return UpdateTokenResponse(
        access_token=tokens["access_token"],
        token_type="bearer",
        access_token_expires=tokens["access_expires"],
        scopes=tokens["scopes"],
    )


# --------------------------------------------------------------------------- #
#  Token revoke                                                               #
# --------------------------------------------------------------------------- #


@router.post("/login/revoke-token")
async def revoke_token(
    session: SessionDep,
    body: RevokeTokenRequest = Body(...),
    current_user: User = Depends(get_current_user),
) -> Message:
    """Revoke a refresh token or all tokens for the current user."""
    # Check if it's a refresh token belonging to this user
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token == body.token,  # type: ignore[arg-type]
            RefreshToken.user_id == current_user.id,  # type: ignore[arg-type]
        )
    )
    stored = result.scalar_one_or_none()

    if stored:
        stored.revoked = True
        await session.commit()
        return Message(message="Refresh token revoked")

    # Try to treat it as an access token - revoke all tokens for this user
    try:
        payload = verify_access_token(body.token)
        if payload and payload.get("sub") == current_user.email:
            await session.execute(
                sa_update(RefreshToken)
                .where(RefreshToken.user_id == current_user.id)  # type: ignore[arg-type]
                .where(RefreshToken.revoked != True)  # type: ignore[arg-type]
                .values(revoked=True)
            )
            await session.commit()
            return Message(message="All tokens revoked")
    except Exception:
        pass

    return Message(message="Token revoked")


# --------------------------------------------------------------------------- #
#  Client credentials flow                                                    #
# --------------------------------------------------------------------------- #


@router.post("/login/client-credentials", response_model=Token)
async def client_credentials_login(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    response: Response = Response(),
) -> Token:
    """OAuth2 client credentials flow for service-to-service auth."""
    # Extract credentials from header or form data (HTTP concern only)
    client_id = request.headers.get("x-client-id")
    client_secret = request.headers.get("x-client-secret")
    if not client_id:
        form = await request.form()
        client_id = form.get("client_id")
        client_secret = form.get("client_secret")

    if not client_id or not client_secret:
        # Try parsing from Authorization header (Basic auth)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Basic "):
            import base64

            decoded = base64.b64decode(auth_header[6:]).decode()
            parts = decoded.split(":", 1)
            if len(parts) == 2:
                client_id, client_secret = parts

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing client credentials",
        )

    # Delegate authentication and token creation to service
    flow_svc = OAuth2FlowService(session)
    client, token_scopes = await flow_svc.authenticate_client(client_id, client_secret)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    access_token, access_expires, refresh_token_str, refresh_expires = (
        await flow_svc.create_client_tokens(client_id, token_scopes)
    )

    AuthTokenService.attach_auth_cookies(response, access_token, refresh_token_str, request)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        access_token_expires=access_expires,
        refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
        scopes=token_scopes,
    )


# --------------------------------------------------------------------------- #
#  Authorization code flow                                                    #
# --------------------------------------------------------------------------- #


@router.post("/login/authorize", response_model=AuthorizationCodeResponse)
async def authorization_code(
    body: AuthorizationCodeChallenge,
    session: AsyncSession = Depends(get_db_session),
) -> AuthorizationCodeResponse:
    """OAuth2 authorization code flow - step 1: obtain an authorization code."""
    flow_svc = OAuth2FlowService(session)
    auth_code, error = await flow_svc.create_authorization_code(
        client_id=body.client_id,
        code_challenge=body.code_challenge,
        redirect_uri=body.redirect_uri,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    return AuthorizationCodeResponse(
        access_token=auth_code,  # type: ignore[arg-type]
        token_type="code",
        expires_in=600,
    )


@router.post("/login/auth-code", response_model=Token)
async def authorization_code_token(
    body: AuthorizationCodeRequest,
    session: AsyncSession = Depends(get_db_session),
    response: Response = Response(),
) -> Token:
    """OAuth2 authorization code flow - step 2: exchange code for tokens (PKCE)."""
    flow_svc = OAuth2FlowService(session)

    access_token, refresh_expires_sec, error, token_scopes = (
        await flow_svc.exchange_authorization_code(
            client_id=body.client_id,
            code=body.code,
            code_verifier=body.code_verifier,
        )
    )
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return Token(
        access_token=access_token,  # type: ignore[arg-type]
        refresh_token="",  # Refresh token stored in DB keyed on client_id
        token_type="bearer",
        access_token_expires=refresh_expires_sec or 0,
        refresh_token_expires=refresh_expires_sec or 0,
        scopes=token_scopes,
    )


# --------------------------------------------------------------------------- #
#  Implicit grant                                                             #
# --------------------------------------------------------------------------- #


@router.post("/login/implicit-token", response_model=ImplicitTokenResponse)
async def implicit_token(
    body: ImplicitTokenRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ImplicitTokenResponse:
    """OAuth2 implicit grant for SPAs - returns access token directly."""
    flow_svc = OAuth2FlowService(session)

    access_token, expires_in_sec, error = await flow_svc.issue_implicit_token(
        client_id=body.client_id,
        code_verifier=body.code_verifier,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    return ImplicitTokenResponse(
        access_token=access_token,  # type: ignore[arg-type]
        token_type="bearer",
        expires_in=expires_in_sec or 0,
    )


# --------------------------------------------------------------------------- #
#  Logout                                                                     #
# --------------------------------------------------------------------------- #


@router.post("/login/logout")
async def logout(
    session: SessionDep, current_user: CurrentUser, response: Response, request: Request
) -> Message:
    """Revoke all tokens and clear auth cookies."""
    token_svc = AuthTokenService(session=session)
    await token_svc.revoke_all_user_tokens(current_user.id)
    AuthTokenService.clear_auth_cookies(response, request)
    return Message(message="Logged out")


# --------------------------------------------------------------------------- #
#  User info                                                                  #
# --------------------------------------------------------------------------- #


@router.get("/auth/me")
async def me(current_user: CurrentUser, session: SessionDep) -> UserPublic:
    """Return current user info without is_superuser."""
    token_svc = AuthTokenService(session=session)
    scopes = await token_svc.resolve_user_scopes(current_user.id)
    return UserPublic(
        email=current_user.email,
        is_active=current_user.is_active,
        id=current_user.id,
        new_id=current_user.new_id,
        full_name=current_user.full_name,
        assigned_scopes=scopes,
    )


# --------------------------------------------------------------------------- #
#  Token inspection                                                           #
# --------------------------------------------------------------------------- #


@router.post("/login/token-scopes", response_model=TokenScopes)
async def token_scopes(
    session: SessionDep,
    token: str = Body(..., embed=True),
) -> TokenScopes:
    """Decode a JWT access token and return its embedded scopes and claims.

    Auth is enforced by validating the presented token itself (401 if invalid).
    """
    try:
        payload = verify_access_token(
            token, audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    scopes = payload.get("scopes") or []
    user_email: str = payload.get("sub", "")  # type: ignore[assignment]
    if user_email:
        stmt = select(User).where(User.email == user_email)  # type: ignore[arg-type]
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    return TokenScopes(
        email=user_email,
        scopes=scopes,
        sub=payload.get("sub"),
        iss=payload.get("iss"),
        aud=payload.get("aud"),
        jti=payload.get("jti"),
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Test access token."""
    return current_user


# --------------------------------------------------------------------------- #
#  Password recovery                                                          #
# --------------------------------------------------------------------------- #


@router.post("/password-recovery")
async def recover_password(
    body: PasswordRecoveryRequest, session: SessionDep, request: Request
) -> Message:
    """Send a password reset email (prevents enumeration)."""
    from app.core.rate_limiter import check_rate_limit, get_client_ip

    ip = get_client_ip(request)
    if not check_rate_limit(f"recovery:{ip}", 3, 60 * 60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

    repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=repository)
    await auth_service.initiate_password_recovery(email=body.email, session=session)

    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: NewPassword, request: Request) -> Message:
    """Reset password using a single-use token from the recovery email."""
    from app.core.rate_limiter import check_rate_limit, get_client_ip

    ip = get_client_ip(request)
    if not check_rate_limit(f"reset:{ip}", 5, 60 * 60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)

    result = await auth_service.reset_password(
        token=body.token, new_password=body.new_password, session=session
    )

    return Message(message=result["message"])


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """Superuser-only endpoint for debugging email templates."""
    import re

    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)
    await auth_service.initiate_password_recovery(email=email, session=session)

    return HTMLResponse(
        content="Password recovery email sent successfully",
        headers={"subject:": "Password Recovery"},
    )


# --------------------------------------------------------------------------- #
#  Module-level helpers                                                       #
# --------------------------------------------------------------------------- #

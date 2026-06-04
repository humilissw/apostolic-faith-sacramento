from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from app.core import security
from app.core.scopes import Scope
from app.config import settings
from app.core.db import get_db_session
from app.core.security import verify_password
from app.models import (
    AuthorizationCode,
    Message,
    NewPassword,
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
from app.repositories.user_scope_repo import UserScopeRepository
from app.services.auth_service import AuthService


def _cookie_kwargs(request: Request) -> dict[str, Any]:
    """Compute cookie kwargs that work across HTTP and HTTPS for cross-origin requests."""
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


@router.post("/login/pkce-challenge")
async def pkce_challenge() -> dict:
    """Generate a PKCE code_verifier and code_challenge pair.

    Clients should store the code_verifier and send the code_challenge
    during the authorization request, then use the verifier during token exchange.
    """
    verifier = security.generate_code_verifier()
    challenge = security.generate_code_challenge(verifier)
    return {
        "code_verifier": verifier,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    *,
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    """
    OAuth2 compatible token login via password grant.
    Sets httpOnly cookies for access_token and refresh_token.
    Returns tokens in JSON body for client-side navigation.
    Rate limited to prevent brute-force attacks.
    """
    # Rate limit check (5 requests per 15 minutes per IP)
    ip = request.client.host if request.client else "unknown"
    from app.core.rate_limiter import check_rate_limit

    if not check_rate_limit(f"login:{ip}", 5, 15 * 60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    repository = UserRepository(session=session)
    user = await repository.get_by_email(email=form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Resolve scopes from DB: superuser scope grants all, otherwise use assigned scopes
    # Users with no assigned scopes get api:all (implicit trust for authenticated users)
    scope_repo = UserScopeRepository(session)
    assigned = await scope_repo.get_scopes(user.id)
    if "superuser" in assigned:
        token_scopes = [s.value for s in Scope]
    else:
        token_scopes = list(set(assigned) | {"api:all"}) if assigned else ["api:all"]

    access_token, access_expires = security.create_access_token_with_claims(
        user.email,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=token_scopes,
    )
    refresh_token, refresh_expires = security.create_refresh_token_with_expiry(
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Store refresh token in database
    db_refresh = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_expires,
    )
    session.add(db_refresh)
    await session.commit()

    # Set httpOnly cookies for browser-based auth
    access_expire_minutes = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire_days = int(settings.REFRESH_TOKEN_EXPIRE_DAYS)
    c = _cookie_kwargs(request)

    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=60 * access_expire_minutes,
        **c,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        max_age=60 * 60 * 24 * refresh_expire_days,
        **c,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        access_token_expires=access_expires,
        refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
        scopes=token_scopes,
    )


@router.post("/login/refresh-token", response_model=UpdateTokenResponse)
async def refresh_token(
    body: TokenRefresh,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    response: Response = Response(),
) -> UpdateTokenResponse:
    """
    Exchange a valid refresh token for a new access token.
    The old refresh token is revoked after use (single-use refresh tokens).
    Sets updated httpOnly cookies.
    """
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token == body.refresh_token,  # type: ignore[arg-type]
            RefreshToken.revoked != True,  # type: ignore[arg-type]
        )
    )
    stored = result.scalar_one_or_none()

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Check if token is expired
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        stored.revoked = True
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    # Get the user
    user = await session.get(User, stored.user_id)
    if user is None or not user.is_active:
        stored.revoked = True
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Revoke the old refresh token (single-use)
    stored.revoked = True
    await session.commit()

    # Issue new access token (superuser scope grants all, otherwise use assigned scopes)
    # Users with no assigned scopes get api:all (implicit trust for authenticated users)
    scope_repo = UserScopeRepository(session)
    assigned = await scope_repo.get_scopes(user.id)
    if "superuser" in assigned:
        new_scopes = [s.value for s in Scope]
    else:
        new_scopes = list(set(assigned) | {"api:all"}) if assigned else ["api:all"]
    new_access_token, new_expires = security.create_access_token_with_claims(
        user.email,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=new_scopes,
    )

    # Issue new refresh token
    new_refresh_token, new_refresh_expires = security.create_refresh_token_with_expiry(
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    new_stored = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=new_refresh_expires,
    )
    session.add(new_stored)
    await session.commit()

    # Update httpOnly cookies with new token values
    access_expire_minutes = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire_days = int(settings.REFRESH_TOKEN_EXPIRE_DAYS)
    c = _cookie_kwargs(request)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=new_access_token,
        max_age=60 * access_expire_minutes,
        **c,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=new_refresh_token,
        max_age=60 * 60 * 24 * refresh_expire_days,
        **c,
    )

    return UpdateTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        access_token_expires=new_expires,
        scopes=new_scopes,
    )


@router.post("/login/revoke-token")
async def revoke_token(
    session: SessionDep,
    body: RevokeTokenRequest = Body(...),
    current_user: User = Depends(get_current_user),
) -> Message:
    """
    Revoke a token (either access or refresh).
    For refresh tokens: marks them as revoked in the database.
    For access tokens (JWT): revokes all refresh tokens for this user.
    """
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
        payload = security.verify_access_token(body.token)
        if payload and payload.get("sub") == current_user.email:
            await session.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == current_user.id)  # type: ignore[arg-type]
                .where(RefreshToken.revoked != True)  # type: ignore[arg-type]
                .values(revoked=True)
            )
            await session.commit()
            return Message(message="All tokens revoked")
    except Exception:
        # Token was not a valid access token either; fall through to generic response
        pass

    return Message(message="Token revoked")


@router.post("/login/client-credentials", response_model=Token)
async def client_credentials_login(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    response: Response = Response(),
) -> Token:
    """OAuth2 client credentials flow for service-to-service auth."""
    from app.models import ClientCredentials

    # Extract credentials from header or form data
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

    result = await session.execute(
        select(ClientCredentials).where(
            ClientCredentials.client_id == client_id,  # type: ignore[arg-type]
            ClientCredentials.is_active == True,  # type: ignore[arg-type]
        )
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    if not security.verify_password(client_secret, client.client_secret_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    token_scopes = client.scopes.split(",") if client.scopes else []

    access_token, access_expires = security.create_access_token_with_claims(
        client_id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=token_scopes,
    )
    refresh_token_str, refresh_expires = security.create_refresh_token_with_expiry(
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # For client credentials, store refresh token keyed on client_id
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == "client:" + client_id  # type: ignore[arg-type]
        )
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
        session.add(db_refresh)
    await session.commit()

    c = _cookie_kwargs(request)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **c,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token_str,
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
        **c,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        access_token_expires=access_expires,
        refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
        scopes=token_scopes,
    )


@router.post("/login/authorize", response_model=AuthorizationCodeResponse)
async def authorization_code(
    body: AuthorizationCodeChallenge,
    session: AsyncSession = Depends(get_db_session),
) -> AuthorizationCodeResponse:
    """OAuth2 authorization code flow - step 1: obtain an authorization code.

    Client calls /login/pkce-challenge to get code_verifier/code_challenge.
    Then calls /login/authorize with client_id + code_challenge to get a code.
    Then calls /login/auth-code with code + code_verifier to get tokens.
    """
    from app.models import ClientCredentials

    result = await session.execute(
        select(ClientCredentials).where(
            ClientCredentials.client_id == body.client_id,  # type: ignore[arg-type]
            ClientCredentials.is_active == True,  # type: ignore[arg-type]
        )  # type: ignore[arg-type]
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    # Store authorization code (opaque random code, not the full JWT)
    import secrets

    auth_code = secrets.token_urlsafe(32)

    db_code = AuthorizationCode(
        code=auth_code,
        client_id=body.client_id,
        code_challenge=body.code_challenge,
        redirect_uri=body.redirect_uri,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    session.add(db_code)
    await session.commit()

    return AuthorizationCodeResponse(
        access_token=auth_code,
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
    from app.models import ClientCredentials

    # Find stored authorization code
    result = await session.execute(
        select(AuthorizationCode).where(
            AuthorizationCode.code == body.code  # type: ignore[arg-type]
        )
    )
    stored = result.scalar_one_or_none()

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code",
        )
    if stored.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code already used",
        )
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code has expired",
        )

    # Verify client_id matches
    result = await session.execute(
        select(ClientCredentials).where(
            ClientCredentials.client_id == body.client_id,  # type: ignore[arg-type]
            ClientCredentials.is_active == True,  # type: ignore[arg-type]
        )  # type: ignore[arg-type]
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    # Verify client_id matches the stored code
    if stored.client_id != body.client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code client_id mismatch",
        )

    # Verify PKCE code_verifier
    expected_challenge = security.generate_code_challenge(body.code_verifier)
    if stored.code_challenge != expected_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE code_challenge mismatch",
        )

    # Issue tokens using client scopes
    scopes_raw = client.scopes  # type: ignore[attr-defined]
    token_scopes = scopes_raw.split(",") if scopes_raw else ["client"]

    access_token, access_expires = security.create_access_token_with_claims(
        body.client_id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=token_scopes,
    )
    refresh_token_str, refresh_expires = security.create_refresh_token_with_expiry(
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Mark code as used
    stored.used = True
    await session.commit()

    # Store refresh token keyed on client_id
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == "client:" + body.client_id  # type: ignore[arg-type]
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.token = refresh_token_str
        existing.expires_at = refresh_expires
        existing.revoked = False
    else:
        db_refresh = RefreshToken(
            user_id="client:" + body.client_id,
            token=refresh_token_str,
            expires_at=refresh_expires,
        )
        session.add(db_refresh)
    await session.commit()

    cookie_secure = settings.COOKIE_SECURE
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite="lax",
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token_str,
        httponly=True,
        secure=cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        access_token_expires=access_expires,
        refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
        scopes=token_scopes,
    )


@router.post("/login/implicit-token", response_model=ImplicitTokenResponse)
async def implicit_token(
    body: ImplicitTokenRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ImplicitTokenResponse:
    """OAuth2 implicit grant for SPAs - returns access token directly.

    For use with single-page applications where a refresh token cannot be stored securely.
    Uses PKCE for enhanced security (RFC 9239).
    """
    from app.models import ClientCredentials

    result = await session.execute(
        select(ClientCredentials).where(
            ClientCredentials.client_id == body.client_id,  # type: ignore[arg-type]
            ClientCredentials.is_active == True,  # type: ignore[arg-type]
        )  # type: ignore[arg-type]
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    # For implicit grant, prioritize spa:all scope
    token_scopes = ["spa:all"]
    if client.scopes:
        client_scopes = client.scopes.split(",")
        # Include client scopes that overlap with known scopes
        known = {s.value for s in Scope}
        token_scopes = [s for s in client_scopes if s in known] or ["spa:all"]

    access_token, access_expires = security.create_access_token_with_claims(
        body.client_id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=token_scopes,
    )

    return ImplicitTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=access_expires,
    )


@router.post("/login/logout")
async def logout(
    session: SessionDep, current_user: CurrentUser, response: Response, request: Request
) -> Message:
    """Revoke all tokens and clear auth cookies."""
    # Revoke all refresh tokens for this user
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == current_user.id)  # type: ignore[arg-type]
        .where(RefreshToken.revoked != True)  # type: ignore[arg-type]
        .values(revoked=True)
    )
    await session.commit()

    # Clear auth cookies
    c = _cookie_kwargs(request)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value="",
        max_age=0,
        **c,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value="",
        max_age=0,
        **c,
    )
    return Message(message="Logged out")


@router.get("/auth/me")
async def me(current_user: CurrentUser, session: SessionDep) -> UserPublic:
    """Return current user info without is_superuser."""
    scope_repo = UserScopeRepository(session)
    scopes = await scope_repo.get_scopes(current_user.id)
    return UserPublic(
        email=current_user.email,
        is_active=current_user.is_active,
        id=current_user.id,
        new_id=current_user.new_id,
        full_name=current_user.full_name,
        assigned_scopes=scopes,
    )


@router.post("/login/token-scopes")
async def token_scopes(
    session: SessionDep,
    token: str = Body(..., embed=True),
) -> TokenScopes:
    """Decode a JWT access token and return its embedded scopes and claims."""
    try:
        payload = security.verify_access_token(
            token, audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    scopes = payload.get("scopes") or []
    # Resolve email from DB to confirm user still exists
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
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(email: str, session: SessionDep, request: Request) -> Message:
    """
    Password Recovery
    Rate limited to prevent email spamming.
    """
    # Rate limit check (3 requests per hour per IP)
    ip = request.client.host if request.client else "unknown"
    from app.core.rate_limiter import check_rate_limit

    if not check_rate_limit(f"recovery:{ip}", 3, 60 * 60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=repository)

    # Use the service to initiate password recovery
    # The service handles the case where user doesn't exist gracefully
    await auth_service.initiate_password_recovery(email=email)

    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    # Create user repository and service
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)

    # Use the service to reset the password
    result = await auth_service.reset_password(
        token=body.token, new_password=body.new_password, session=session
    )

    # Return the success message
    return Message(message=result["message"])


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    # Create user repository and service
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)

    # Use the service to initiate password recovery
    await auth_service.initiate_password_recovery(email=email)

    # Return HTML content
    return HTMLResponse(
        content="Password recovery email sent successfully",
        headers={"subject:": "Password Recovery"},
    )

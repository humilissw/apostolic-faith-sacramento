from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
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
    Message,
    NewPassword,
    RefreshToken,
    RevokeTokenRequest,
    Token,
    TokenRefresh,
    UpdateTokenResponse,
    User,
    UserPublic,
)
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(tags=["login"])


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

    # Resolve scopes: superusers get all, regular users get requested scopes
    requested_scopes = form_data.scopes if form_data.scopes else ["api:all"]
    if user.is_superuser:
        token_scopes = [s.value for s in Scope]
    else:
        token_scopes = requested_scopes

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
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * access_expire_minutes,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * refresh_expire_days,
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

    # Issue new access token (superusers get all scopes, regular users get api:all)
    new_scopes = [s.value for s in Scope] if user.is_superuser else ["api:all"]
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
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * access_expire_minutes,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * refresh_expire_days,
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


@router.post("/login/logout")
async def logout_via_idp(current_user: CurrentUser) -> Message:
    return Message(message="Logged out via idp")


@router.post("/login/clear")
async def clear_token(current_user: CurrentUser) -> Message:
    return Message(message="Token cleared")


@router.post("/login/logout")
async def logout(
    session: SessionDep,
    current_user: CurrentUser,
    response: Response,
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
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,
        path="/",
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,
        path="/",
    )
    return Message(message="Logged out")


@router.get("/auth/me")
async def me(current_user: CurrentUser) -> User:
    """Return current user info. Validates the auth cookie."""
    return current_user


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

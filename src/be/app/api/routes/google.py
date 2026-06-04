from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import CurrentUser, SessionDep
from app.config import settings
from app.core import security
from app.core.scopes import Scope
from app.models import Message, RefreshToken, UserCreate
from app.repositories.user_repo import UserRepository
from app.repositories.user_scope_repo import UserScopeRepository
from sqlalchemy import update as sa_update

router = APIRouter(prefix="/google", tags=["authentication"])


def _build_oauth():
    """Build an OAuth instance with Google credentials from settings."""
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


@router.get("/login/google")
async def login_via_google(request: Request) -> RedirectResponse:
    """Redirect to Google's OAuth 2.0 authorization page with PKCE."""
    oauth = _build_oauth()

    # Generate PKCE code_verifier and challenge
    code_verifier = security.generate_code_verifier()
    code_challenge = security.generate_code_challenge(code_verifier)

    # Store code_verifier in a secure, http-only cookie
    redirect = await oauth.google.authorize_redirect(
        request,
        redirect_uri=f"{settings.DOMAIN}{settings.API_V1_STR}/google/auth/google",
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )

    redirect.set_cookie(
        key="google_code_verifier",
        value=code_verifier,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=300,
    )
    return redirect


@router.get("/auth/google")
async def auth_via_google(
    request: Request,
    session: SessionDep,
) -> RedirectResponse:
    """
    Google OAuth 2.0 callback with PKCE.
    Verifies the Google ID token, issues our JWT tokens,
    and redirects to the frontend callback page.
    """
    # Extract the code_verifier from the http-only cookie
    code_verifier = request.cookies.get("google_code_verifier")
    if not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE verification failed. Please try again.",
        )

    oauth = _build_oauth()

    # Verify code and extract ID token (authlib verifies PKCE automatically)
    token = await oauth.google.authorize_access_token(request)

    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return an ID token",
        )

    # Verify ID token against Google's public keys (run in executor to avoid blocking)
    import asyncio
    from google.auth import jwt as google_jwt

    credentials, payload = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: google_jwt.verify_id_token(id_token, settings.GOOGLE_CLIENT_ID),
    )

    email = payload.get("email")
    if not email or not payload.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email not verified",
        )

    # Find or create user in our database
    repository = UserRepository(session=session)
    user = await repository.get_by_email(email=email)

    if user is None:
        import secrets

        user_in = UserCreate(
            email=email,
            full_name=payload.get("name", ""),
            password=secrets.token_urlsafe(16),
            is_active=True,
            is_superuser=False,
        )
        from app.crud import create_user

        user = await create_user(session=session, user_create=user_in)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Issue our own tokens (superuser scope grants all, otherwise use assigned scopes)
    scope_repo = UserScopeRepository(session)
    db_scopes = await scope_repo.get_scopes(user.id)
    if "superuser" in db_scopes:
        user_scopes = [s.value for s in Scope]
    elif db_scopes:
        user_scopes = db_scopes
    else:
        user_scopes = ["api:all"]
    access_token, access_expires = security.create_access_token_with_claims(
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
    session.add(db_refresh)
    await session.commit()

    # Clear the code_verifier cookie (one-time use)
    redirect = RedirectResponse(url=f"{settings.FRONTEND_HOST}/login/", status_code=302)
    redirect.delete_cookie("google_code_verifier")

    # Set httpOnly session cookies — the callback page verifies via /auth/me
    scopes_param = ",".join(user_scopes)
    redirect = RedirectResponse(
        url=f"{settings.FRONTEND_HOST}/google-callback?scopes={scopes_param}",
        status_code=302,
    )
    redirect.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    redirect.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token_str,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return redirect


@router.post("/logout")
async def google_logout(current_user: CurrentUser, session: SessionDep) -> Message:
    """Revoke all refresh tokens for the current user."""
    await session.execute(
        sa_update(RefreshToken)
        .where(RefreshToken.user_id == current_user.id)  # type: ignore[arg-type]
        .where(RefreshToken.revoked != True)  # type: ignore[arg-type]
        .values(revoked=True)
    )
    await session.commit()
    return Message(message="Logged out via Google")

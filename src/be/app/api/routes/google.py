"""Google OAuth authentication routes."""

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import CurrentUser, SessionDep
from app.config import settings
from app.models import Message
from app.services.google_auth_service import GoogleAuthService

router = APIRouter(prefix="/google", tags=["authentication"])


@router.get("/login/google")
async def login_via_google(request: Request) -> RedirectResponse:
    """Redirect to Google's OAuth 2.0 authorization page with PKCE."""
    svc = GoogleAuthService(session=None)  # session not needed for this step

    code_verifier, code_challenge = await svc.generate_pkce_pair()

    oauth = await svc.build_oauth()

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
    """Google OAuth 2.0 callback with PKCE."""
    # Extract the code_verifier from the http-only cookie (HTTP concern only)
    code_verifier = request.cookies.get("google_code_verifier")
    if not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE verification failed. Please try again.",
        )

    svc = GoogleAuthService(session)

    # Verify code and extract ID token (authlib verifies PKCE automatically)
    oauth = await svc.build_oauth()
    token = await oauth.google.authorize_access_token(request)

    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return an ID token",
        )

    # Delegate ID token verification to service
    payload = await svc.verify_google_id_token(id_token)

    # Delegate user lookup/creation to service
    user = await svc.get_or_create_user_from_google(
        email=payload["email"],
        full_name=payload.get("name", ""),
    )

    # Delegate token creation to service
    access_token, refresh_token_str = await svc.create_tokens_for_user(user)

    # Build redirect response (HTTP concern only)
    scopes_param = ",".join(await svc.resolve_user_scopes(user.id))
    redirect = RedirectResponse(
        url=f"{settings.FRONTEND_HOST}/google-callback?scopes={scopes_param}",
        status_code=302,
    )
    redirect.delete_cookie("google_code_verifier")

    # Set httpOnly session cookies
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
    svc = GoogleAuthService(session)
    return await svc.google_logout(current_user)

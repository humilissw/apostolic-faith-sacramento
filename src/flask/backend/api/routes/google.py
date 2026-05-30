"""Google OAuth routes - converted from FastAPI to Flask."""

from datetime import timedelta

from flask import Blueprint, jsonify, make_response, redirect, request

from backend.api.deps import get_current_user, get_db
from backend.config import settings
from backend.core import security
from backend.core.scopes import Scope
from backend.models import RefreshToken, UserCreate
from backend.repositories.user_repo import UserRepository
from backend.repositories.user_scope_repo import UserScopeRepository

router = Blueprint("google", __name__)


def _build_oauth():
    """Build an OAuth instance with Google credentials from settings."""
    from authlib.integrations.requests_client import OAuth2Session

    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "dummy":
        return None
    oauth = OAuth2Session(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scope="openid email profile",
    )
    return oauth


@router.route("/google/login/google")
def login_via_google():
    _tag = "authentication"
    oauth = _build_oauth()
    if oauth is None:
        return (
            jsonify(
                {
                    "detail": ("Google OAuth is not configured. " "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."),
                }
            ),
            501,
        )

    code_verifier = security.generate_code_challenge("verifier_placeholder")[:43]
    import secrets

    code_verifier = secrets.token_urlsafe(32)
    code_challenge = security.generate_code_challenge(code_verifier)

    authorize_url = oauth.build_authorize_url(
        redirect_uri=f"{settings.DOMAIN}{settings.API_V1_STR}/google/auth/google",
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )

    resp = redirect(authorize_url, 302)
    resp.set_cookie(
        "google_code_verifier",
        code_verifier,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=300,
    )
    return resp


@router.route("/google/auth/google")
def auth_via_google():
    _tag = "authentication"
    code_verifier = request.cookies.get("google_code_verifier")
    if not code_verifier:
        return jsonify({"detail": "PKCE verification failed. Please try again."}), 400

    oauth = _build_oauth()
    if oauth is None:
        return jsonify({"detail": "Google OAuth not configured"}), 501

    code = request.args.get("code")
    if not code:
        return jsonify({"detail": "Missing authorization code"}), 400

    token = oauth.fetch_token(
        f"{settings.DOMAIN}{settings.API_V1_STR}/google/auth/google",
        code=code,
        code_verifier=code_verifier,
    )

    id_token = token.get("id_token")
    if not id_token:
        return jsonify({"detail": "Google did not return an ID token"}), 400

    from google.auth import jwt as google_jwt

    credentials, payload = google_jwt.verify_id_token(id_token, settings.GOOGLE_CLIENT_ID)

    email = payload.get("email")
    if not email or not payload.get("email_verified"):
        return jsonify({"detail": "Google email not verified"}), 400

    session = get_db()
    repository = UserRepository(session=session)
    user = repository.get_by_email(email=email)

    if user is None:
        import secrets

        user_in = UserCreate(
            email=email,
            full_name=payload.get("name", ""),
            password=secrets.token_urlsafe(16),
            is_active=True,
            is_superuser=False,
        )
        from backend.crud import create_user as crud_create_user

        user = crud_create_user(session=session, user_create=user_in)
        session.add(user)
        session.commit()
        session.refresh(user)
    elif not user.is_active:
        return jsonify({"detail": "Inactive user"}), 400

    scope_repo = UserScopeRepository(session)
    db_scopes = scope_repo.get_scopes(user.id)
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
    session.commit()

    redirect_url = f"{settings.FRONTEND_HOST}/google-callback?scopes={','.join(user_scopes)}"
    resp = make_response(redirect(redirect_url, 302))
    resp.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    resp.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token_str,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    resp.delete_cookie("google_code_verifier")
    return resp


@router.route("/google/logout", methods=["POST"])
def google_logout():
    _tag = "authentication"
    session = get_db()
    current_user = get_current_user()
    from sqlalchemy import update as sa_update

    session.execute(sa_update(RefreshToken).where(RefreshToken.user_id == current_user.id).where(RefreshToken.revoked != True).values(revoked=True))
    session.commit()
    return jsonify({"message": "Logged out via Google"})

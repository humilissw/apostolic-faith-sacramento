"""OAuth2 login routes - converted from FastAPI to Flask."""

from datetime import datetime, timedelta, timezone
import secrets

from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import select, update

from backend.api.deps import get_current_user, get_db, require_scope
from backend.core import security
from backend.core.scopes import Scope
from backend.config import settings
from backend.core.security import verify_password
from backend.models import (
    AuthorizationCode,
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
from backend.repositories.user_repo import UserRepository
from backend.repositories.user_scope_repo import UserScopeRepository
from backend.services.auth_service import AuthService
from pydantic import BaseModel

router = Blueprint("login", __name__)


def _cookie_kwargs(req):
    scheme = req.scheme
    secure = scheme == "https"
    samesite = "none" if secure else "lax"
    return {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "path": settings.COOKIE_PATH,
        "domain": settings.COOKIE_DOMAIN,
    }


class AuthorizationCodeRequest(BaseModel):
    client_id: str
    code: str
    code_verifier: str
    redirect_uri: str = ""


class AuthorizationCodeChallenge(BaseModel):
    client_id: str
    code_challenge: str
    redirect_uri: str = ""


class AuthorizationCodeResponse(BaseModel):
    access_token: str
    token_type: str = "code"
    expires_in: int = 600
    scope: str = ""


class ImplicitTokenRequest(BaseModel):
    client_id: str
    code_challenge: str
    code_verifier: str
    redirect_uri: str = ""


class ImplicitTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str = ""


@router.route("/login/pkce-challenge", methods=["POST"])
def pkce_challenge():
    _tag = "login"
    verifier = security.generate_code_verifier()
    challenge = security.generate_code_challenge(verifier)
    return jsonify({"code_verifier": verifier, "code_challenge": challenge, "code_challenge_method": "S256"})


@router.route("/login/access-token", methods=["POST"])
def login_access_token():
    _tag = "login"
    form_data = request.form
    email = form_data.get("username", "")
    password = form_data.get("password", "")
    if not email or not password:
        return jsonify({"detail": "Missing username or password"}), 422
    session = get_db()
    repository = UserRepository(session=session)
    user = repository.get_by_email(email=email)
    if user is None:
        return jsonify({"detail": "Incorrect email or password"}), 400
    if not verify_password(password, user.hashed_password):
        return jsonify({"detail": "Incorrect email or password"}), 400
    elif not user.is_active:
        return jsonify({"detail": "Inactive user"}), 400
    scope_repo = UserScopeRepository(session)
    assigned = scope_repo.get_scopes(user.id)
    if "superuser" in assigned:
        token_scopes = [s.value for s in Scope]
    else:
        token_scopes = list(set(assigned) | {"api:all"}) if assigned else ["api:all"]
    access_token, access_expires = security.create_access_token_with_claims(
        user.email, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), scopes=token_scopes
    )
    refresh_token, refresh_expires = security.create_refresh_token_with_expiry(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    db_refresh = RefreshToken(user_id=user.id, token=refresh_token, expires_at=refresh_expires)
    session.add(db_refresh)
    session.commit()
    resp = make_response(
        jsonify(
            Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                access_token_expires=access_expires,
                refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
                scopes=token_scopes,
            ).model_dump()
        )
    )
    c = _cookie_kwargs(request)
    resp.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **c,
    )
    resp.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
        **c,
    )
    return resp


@router.route("/login/refresh-token", methods=["POST"])
def refresh_token():
    _tag = "login"
    data = request.get_json()
    body = TokenRefresh(**data)
    if not body.refresh_token:
        return jsonify({"detail": "Missing refresh_token"}), 422
    if len(body.refresh_token) < 8:
        return jsonify({"detail": "Invalid or expired refresh token"}), 401
    session = get_db()
    result = session.execute(select(RefreshToken).where(RefreshToken.token == body.refresh_token, RefreshToken.revoked != True))
    stored = result.scalar_one_or_none()
    if stored is None:
        return jsonify({"detail": "Invalid or expired refresh token"}), 401
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        stored.revoked = True
        session.commit()
        return jsonify({"detail": "Refresh token has expired"}), 401
    user = session.get(User, stored.user_id)
    if user is None or not user.is_active:
        stored.revoked = True
        session.commit()
        return jsonify({"detail": "User not found or inactive"}), 401
    stored.revoked = True
    session.commit()
    scope_repo = UserScopeRepository(session)
    assigned = scope_repo.get_scopes(user.id)
    if "superuser" in assigned:
        new_scopes = [s.value for s in Scope]
    else:
        new_scopes = list(set(assigned) | {"api:all"}) if assigned else ["api:all"]
    new_access_token, new_expires = security.create_access_token_with_claims(
        user.email, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), scopes=new_scopes
    )
    new_refresh_token, new_refresh_expires = security.create_refresh_token_with_expiry(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    new_stored = RefreshToken(user_id=user.id, token=new_refresh_token, expires_at=new_refresh_expires)
    session.add(new_stored)
    session.commit()
    resp = make_response(
        jsonify(
            UpdateTokenResponse(
                access_token=new_access_token,
                token_type="bearer",
                access_token_expires=new_expires,
                scopes=new_scopes,
            ).model_dump()
        )
    )
    c = _cookie_kwargs(request)
    resp.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        new_access_token,
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **c,
    )
    resp.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        new_refresh_token,
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
        **c,
    )
    return resp


@router.route("/login/revoke-token", methods=["POST"])
def revoke_token():
    _tag = "login"
    data = request.get_json()
    body = RevokeTokenRequest(**data)
    session = get_db()
    current_user = get_current_user()
    result = session.execute(select(RefreshToken).where(RefreshToken.token == body.token, RefreshToken.user_id == current_user.id))
    stored = result.scalar_one_or_none()
    if stored:
        stored.revoked = True
        session.commit()
        return jsonify({"message": "Refresh token revoked"})
    try:
        payload = security.verify_access_token(body.token)
        if payload and payload.get("sub") == current_user.email:
            session.execute(update(RefreshToken).where(RefreshToken.user_id == current_user.id, RefreshToken.revoked != True).values(revoked=True))
            session.commit()
            return jsonify({"message": "All tokens revoked"})
    except Exception:
        pass
    return jsonify({"message": "Token revoked"})


@router.route("/login/client-credentials", methods=["POST"])
def client_credentials_login():
    _tag = "login"
    session = get_db()
    client_id = request.headers.get("x-client-id")
    client_secret = request.headers.get("x-client-secret")
    if not client_id:
        client_id = request.form.get("client_id")
        client_secret = request.form.get("client_secret")
    if not client_id:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Basic "):
            import base64

            decoded = base64.b64decode(auth_header[6:]).decode()
            parts = decoded.split(":", 1)
            if len(parts) == 2:
                client_id, client_secret = parts
    if not client_id or not client_secret:
        return jsonify({"detail": "Missing client credentials"}), 401
    from backend.models import ClientCredentials

    result = session.execute(select(ClientCredentials).where(ClientCredentials.client_id == client_id, ClientCredentials.is_active == True))
    client = result.scalar_one_or_none()
    if client is None:
        return jsonify({"detail": "Invalid client credentials"}), 401
    if not verify_password(client_secret, client.client_secret_hash):
        return jsonify({"detail": "Invalid client credentials"}), 401
    token_scopes = client.scopes.split(",") if client.scopes else []
    access_token, access_expires = security.create_access_token_with_claims(
        client_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), scopes=token_scopes
    )
    refresh_token_str, refresh_expires = security.create_refresh_token_with_expiry(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    result = session.execute(select(RefreshToken).where(RefreshToken.user_id == "client:" + client_id))
    existing = result.scalar_one_or_none()
    if existing:
        existing.token = refresh_token_str
        existing.expires_at = refresh_expires
        existing.revoked = False
    else:
        db_refresh = RefreshToken(user_id="client:" + client_id, token=refresh_token_str, expires_at=refresh_expires)
        session.add(db_refresh)
    session.commit()
    resp = make_response(
        jsonify(
            Token(
                access_token=access_token,
                refresh_token=refresh_token_str,
                token_type="bearer",
                access_token_expires=access_expires,
                refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
                scopes=token_scopes,
            ).model_dump()
        )
    )
    c = _cookie_kwargs(request)
    resp.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **c,
    )
    resp.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token_str,
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
        **c,
    )
    return resp


@router.route("/login/authorize", methods=["POST"])
def authorization_code():
    _tag = "login"
    from backend.models import ClientCredentials

    data = request.get_json()
    body = AuthorizationCodeChallenge(**data)
    session = get_db()
    result = session.execute(select(ClientCredentials).where(ClientCredentials.client_id == body.client_id, ClientCredentials.is_active == True))
    client = result.scalar_one_or_none()
    if client is None:
        return jsonify({"detail": "Invalid client credentials"}), 401
    auth_code = secrets.token_urlsafe(32)
    db_code = AuthorizationCode(
        code=auth_code,
        client_id=body.client_id,
        code_challenge=body.code_challenge,
        redirect_uri=body.redirect_uri,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    session.add(db_code)
    session.commit()
    return jsonify(AuthorizationCodeResponse(access_token=auth_code, token_type="code", expires_in=600).model_dump())


@router.route("/login/auth-code", methods=["POST"])
def authorization_code_token():
    _tag = "login"
    from backend.models import ClientCredentials

    data = request.get_json()
    body = AuthorizationCodeRequest(**data)
    session = get_db()
    result = session.execute(select(AuthorizationCode).where(AuthorizationCode.code == body.code))
    stored = result.scalar_one_or_none()
    if stored is None:
        return jsonify({"detail": "Invalid authorization code"}), 400
    if stored.used:
        return jsonify({"detail": "Authorization code already used"}), 400
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        return jsonify({"detail": "Authorization code has expired"}), 400
    result = session.execute(select(ClientCredentials).where(ClientCredentials.client_id == body.client_id, ClientCredentials.is_active == True))
    client = result.scalar_one_or_none()
    if client is None:
        return jsonify({"detail": "Invalid client credentials"}), 401
    if stored.client_id != body.client_id:
        return jsonify({"detail": "Authorization code client_id mismatch"}), 400
    expected_challenge = security.generate_code_challenge(body.code_verifier)
    if stored.code_challenge != expected_challenge:
        return jsonify({"detail": "PKCE code_challenge mismatch"}), 400
    scopes_raw = client.scopes
    token_scopes = scopes_raw.split(",") if scopes_raw else ["client"]
    access_token, access_expires = security.create_access_token_with_claims(
        body.client_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), scopes=token_scopes
    )
    refresh_token_str, refresh_expires = security.create_refresh_token_with_expiry(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    stored.used = True
    session.commit()
    result = session.execute(select(RefreshToken).where(RefreshToken.user_id == "client:" + body.client_id))
    existing = result.scalar_one_or_none()
    if existing:
        existing.token = refresh_token_str
        existing.expires_at = refresh_expires
        existing.revoked = False
    else:
        db_refresh = RefreshToken(user_id="client:" + body.client_id, token=refresh_token_str, expires_at=refresh_expires)
        session.add(db_refresh)
    session.commit()
    resp = make_response(
        jsonify(
            Token(
                access_token=access_token,
                refresh_token=refresh_token_str,
                token_type="bearer",
                access_token_expires=access_expires,
                refresh_token_expires=int((refresh_expires - datetime.now(timezone.utc)).total_seconds()),
                scopes=token_scopes,
            ).model_dump()
        )
    )
    resp.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    resp.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token_str,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60 * 24 * int(settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return resp


@router.route("/login/implicit-token", methods=["POST"])
def implicit_token():
    _tag = "login"
    from backend.models import ClientCredentials

    data = request.get_json()
    body = ImplicitTokenRequest(**data)
    session = get_db()
    result = session.execute(select(ClientCredentials).where(ClientCredentials.client_id == body.client_id, ClientCredentials.is_active == True))
    client = result.scalar_one_or_none()
    if client is None:
        return jsonify({"detail": "Invalid client credentials"}), 401
    token_scopes = ["spa:all"]
    if client.scopes:
        client_scopes = client.scopes.split(",")
        known = {s.value for s in Scope}
        token_scopes = [s for s in client_scopes if s in known] or ["spa:all"]
    access_token, access_expires = security.create_access_token_with_claims(
        body.client_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), scopes=token_scopes
    )
    return jsonify(ImplicitTokenResponse(access_token=access_token, token_type="bearer", expires_in=access_expires).model_dump())


@router.route("/login/logout", methods=["POST"])
def logout():
    _tag = "login"
    session = get_db()
    current_user = get_current_user()
    session.execute(update(RefreshToken).where(RefreshToken.user_id == current_user.id, RefreshToken.revoked != True).values(revoked=True))
    session.commit()
    resp = make_response(jsonify({"message": "Logged out"}))
    c = _cookie_kwargs(request)
    resp.set_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, "", max_age=0, **c)
    resp.set_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, "", max_age=0, **c)
    return resp


@router.route("/auth/me")
def me():
    _tag = "login"
    session = get_db()
    current_user = get_current_user()
    scope_repo = UserScopeRepository(session)
    scopes = scope_repo.get_scopes(current_user.id)
    return jsonify(
        UserPublic(
            email=current_user.email,
            is_active=current_user.is_active,
            id=current_user.id,
            new_id=current_user.new_id,
            full_name=current_user.full_name,
            assigned_scopes=scopes,
        ).model_dump()
    )


@router.route("/login/token-scopes", methods=["POST"])
def token_scopes():
    _tag = "login"
    session = get_db()
    data = request.get_json()
    token = data.get("token", "")
    try:
        payload = security.verify_access_token(token, audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER)
    except Exception:
        return jsonify({"detail": "Invalid or expired token"}), 401
    scopes = payload.get("scopes") or []
    user_email = payload.get("sub", "")
    if user_email:
        stmt = select(User).where(User.email == user_email)
        result = session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return jsonify({"detail": "User not found"}), 404
    return jsonify(
        TokenScopes(
            email=user_email,
            scopes=scopes,
            sub=payload.get("sub"),
            iss=payload.get("iss"),
            aud=payload.get("aud"),
            jti=payload.get("jti"),
        ).model_dump()
    )


@router.route("/login/test-token", methods=["POST"])
@require_scope("api:all")
def test_token():
    _tag = "login"
    current_user = get_current_user()
    scope_repo = UserScopeRepository(get_db())
    scopes = scope_repo.get_scopes(current_user.id)
    return jsonify(
        UserPublic(
            email=current_user.email,
            is_active=current_user.is_active,
            id=current_user.id,
            new_id=current_user.new_id,
            full_name=current_user.full_name,
            assigned_scopes=scopes,
        ).model_dump()
    )


@router.route("/password-recovery/<email>", methods=["POST"])
def recover_password(email: str):
    _tag = "login"
    from backend.core.rate_limiter import check_rate_limit

    ip = request.remote_addr
    if not check_rate_limit(f"recovery:{ip}", 3, 60 * 60):
        return jsonify({"detail": "Rate limit exceeded. Please try again later."}), 429
    session = get_db()
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)
    auth_service.initiate_password_recovery(email=email)
    return jsonify({"message": "Password recovery email sent"})


@router.route("/reset-password/", methods=["POST"])
def reset_password():
    _tag = "login"
    session = get_db()
    data = request.get_json()
    body = NewPassword(**data)
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)
    try:
        result = auth_service.reset_password(token=body.token, new_password=body.new_password, session=session)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
    return make_response(jsonify({"message": result["message"]}), 200)


@router.route("/password-recovery-html-content/<email>", methods=["POST"])
def recover_password_html_content(email: str):
    _tag = "login"
    session = get_db()
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)
    auth_service.initiate_password_recovery(email=email)
    return jsonify({"message": "Password recovery email sent successfully"})

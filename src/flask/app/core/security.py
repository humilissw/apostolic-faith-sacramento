from datetime import datetime, timedelta, timezone
import uuid

import jwt
from pwdlib import PasswordHash

from app.config import settings

password_hash = PasswordHash.recommended()

ALGORITHM = "RS256"

PRIVATE_KEY = open(settings.rsa_private_key, "r").read()
PUBLIC_KEY = open(settings.rsa_pub_key, "r").read()


def create_access_token(subject: str, expires_delta: timedelta) -> str:
    try:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(payload=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM)
        verify_access_token(encoded_jwt)
        return str(encoded_jwt)
    except Exception as err:
        print(err)
        raise err


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def verify_access_token(token: str, audience: str | None = None, issuer: str | None = None) -> dict:
    """Verifies a JWT token using the public key."""
    decode_kwargs = {"audience": audience, "issuer": issuer}
    filtered = {k: v for k, v in decode_kwargs.items() if v is not None}
    return dict(jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], **filtered))


def create_refresh_token() -> str:
    """Create a cryptographically secure refresh token."""
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_code_verifier() -> str:
    """Generate a PKCE code_verifier (43-128 characters, URL-safe)."""
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_code_challenge(verifier: str) -> str:
    """Generate a PKCE code_challenge using S256 method."""
    import hashlib
    import base64

    sha256_hash = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(sha256_hash).rstrip(b"=").decode("ascii")


def create_access_token_with_claims(
    subject: str,
    expires_delta: timedelta | None = None,
    scopes: list[str] | None = None,
) -> tuple[str, int]:
    """Create an access token with iss, aud, jti, and scopes claims."""
    expire_delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expire_delta
    jti = str(uuid.uuid4())
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "jti": jti,
        "scopes": scopes or [],
    }
    encoded_jwt = jwt.encode(payload=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM)
    expires_in = int(expire_delta.total_seconds())
    return str(encoded_jwt), expires_in


def create_refresh_token_with_expiry(
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    """Create a refresh token and its expiry datetime."""
    token = create_refresh_token()
    expire_delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expires_at = datetime.now(timezone.utc) + expire_delta
    return token, expires_at

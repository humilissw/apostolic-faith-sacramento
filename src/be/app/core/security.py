from datetime import datetime, timedelta, timezone
import uuid

import jwt
from pwdlib import PasswordHash

from app.config import settings
from app.models import User

password_hash = PasswordHash.recommended()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ALGORITHM = "HS256"
ALGORITHM = "RS256"

# def create_access_token(data: dict):
#     """Generates a new JWT token signed with the private key."""
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     # Sign the token using the private key and RS256 algorithm
#     encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def verify_access_token(token: str):
#     """Verifies a JWT token using the public key."""
#     try:
#         # Decode/verify the token using the public key
#         decoded_payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
#         return decoded_payload
#     except jwt.ExpiredSignatureError:
#         # Handle expired tokens
#         return None
#     except jwt.InvalidTokenError:
#         # Handle all other token validation errors
#         return None

# directories = os.listdir("security_keys/")

# for directory in directories:
#     print(directory)

PRIVATE_KEY = open(settings.rsa_private_key, "r").read()
PUBLIC_KEY = open(settings.rsa_pub_key, "r").read()
# print(PUBLIC_KEY, PRIVATE_KEY)
ALGORITHM = "RS256"

# pem = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo
# )


def create_access_token(subject: str, expires_delta: timedelta) -> str:
    try:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            payload=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM
        )  # type: ignore[return-value]
        verify_access_token(encoded_jwt)
        return str(encoded_jwt)
    except Exception as err:
        print(err)
        raise err


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)


def verify_access_token(token: str, audience: str | None = None, issuer: str | None = None) -> dict:
    """Verifies a JWT token using the public key.

    Returns the decoded payload dict, or raises InvalidTokenError on failure.
    Only verifies aud/iss when the corresponding param is passed.
    """
    decode_kwargs: dict = {"audience": audience, "issuer": issuer}
    # Only pass params that were explicitly provided
    filtered = {k: v for k, v in decode_kwargs.items() if v is not None}
    return dict(jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], **filtered))


def create_refresh_token() -> str:
    """Create a cryptographically secure refresh token (opaque, not a JWT)."""
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_code_verifier() -> str:
    """Generate a PKCE code_verifier (43-128 characters, URL-safe)."""
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_code_challenge(verifier: str) -> str:
    """Generate a PKCE code_challenge using S256 method (recommended)."""
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
    encoded_jwt = jwt.encode(  # type: ignore[return-value]
        payload=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM
    )
    expires_in = int(expire_delta.total_seconds())
    return str(encoded_jwt), expires_in


def create_refresh_token_with_expiry(
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    """Create a refresh token and its expiry datetime.

    Returns (token_string, expires_at).
    """
    token = create_refresh_token()
    expire_delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expires_at = datetime.now(timezone.utc) + expire_delta
    return token, expires_at


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# @app.post("/token")
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# ) -> Token:
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")

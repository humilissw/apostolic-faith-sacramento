from datetime import datetime, timedelta, timezone
import os
from typing import Annotated, Any

from fastapi import Depends, HTTPException
import jwt
from passlib.context import CryptContext
from pwdlib import PasswordHash

import app
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

directories = os.listdir("security_keys/")

for directory in directories:
    print(directory)

PRIVATE_KEY = open("security_keys/private_dec.pem", "r").read()
PUBLIC_KEY = open("security_keys/public_key.pem", "r").read()
print(PUBLIC_KEY, PRIVATE_KEY)
ALGORITHM = "RS256"

# pem = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo
# )

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    try:    
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(payload=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM)
        verify_access_token(encoded_jwt)
        return encoded_jwt
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
    
def verify_access_token(token: str):
    """Verifies a JWT token using the public key."""
    try:
        # Decode/verify the token using the public key
        decoded_payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        # Handle expired tokens
        return None
    except jwt.InvalidTokenError:
        # Handle all other token validation errors
        return None


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

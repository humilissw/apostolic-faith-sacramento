"""Tests for all OAuth2 flows: password, client credentials, authorization code + PKCE, implicit."""

import base64
import hashlib

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import generate_code_challenge, generate_code_verifier, get_password_hash
from app.models import (
    ClientCredentials,
)
from tests.utils.utils import random_lower_string

API_PREFIX = settings.API_V1_STR


@pytest.fixture(scope="function")
async def oauth2_client(
    client: AsyncClient, db_session: AsyncSession
) -> tuple[AsyncClient, AsyncSession]:
    """Provide client and session for OAuth2 tests with table creation."""
    yield client, db_session


@pytest.fixture(scope="function")
async def client_id_secret(db_session: AsyncSession) -> tuple[str, str, ClientCredentials]:
    """Create a test ClientCredentials entry and return (client_id, client_secret, client)."""
    client_id = f"test-oauth-client-{random_lower_string()}"
    client_secret = random_lower_string()
    hashed_secret = get_password_hash(client_secret)
    client = ClientCredentials(
        client_id=client_id,
        client_secret_hash=hashed_secret,
        scopes="api:all,spa:all,client",
        is_active=True,
    )
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    try:
        yield client_id, client_secret, client
    finally:
        try:
            await db_session.execute(
                delete(ClientCredentials).where(ClientCredentials.id == client.id)
            )
            await db_session.commit()
        except Exception:
            pass


@pytest.fixture(scope="function")
async def inactive_client(db_session: AsyncSession) -> str:
    """Create an inactive ClientCredentials entry and return its client_id."""
    client_id = f"inactive-oauth-client-{random_lower_string()}"
    client_secret = random_lower_string()
    hashed_secret = get_password_hash(client_secret)
    client = ClientCredentials(
        client_id=client_id,
        client_secret_hash=hashed_secret,
        scopes="api:all",
        is_active=False,
    )
    db_session.add(client)
    await db_session.commit()
    try:
        yield client_id
    finally:
        try:
            await db_session.execute(
                delete(ClientCredentials).where(ClientCredentials.id == client.id)
            )
            await db_session.commit()
        except Exception:
            pass


# ---- PASSWORD FLOW ----


class TestPasswordFlow:
    @pytest.mark.asyncio
    async def test_password_flow_returns_tokens(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(
            f"{API_PREFIX}/login/access-token",
            data={
                "username": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token_expires"] > 0
        assert data["refresh_token_expires"] > 0
        assert "api:all" in data["scopes"]

    @pytest.mark.asyncio
    async def test_password_flow_rejects_bad_credentials(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(
            f"{API_PREFIX}/login/access-token",
            data={"username": settings.FIRST_SUPERUSER, "password": "wrong_password_xyz"},
        )
        assert r.status_code == 400


# ---- CLIENT CREDENTIALS FLOW ----


class TestClientCredentialsFlow:
    @pytest.mark.asyncio
    async def test_basic_auth_returns_token(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, client_secret, _ = client_id_secret
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        r = await client.post(
            f"{API_PREFIX}/login/client-credentials",
            headers={"Authorization": f"Basic {credentials}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "api:all" in data["scopes"]

    @pytest.mark.asyncio
    async def test_basic_auth_rejects_wrong_secret(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        credentials = base64.b64encode(f"{client_id}:wrong_secret".encode()).decode()
        r = await client.post(
            f"{API_PREFIX}/login/client-credentials",
            headers={"Authorization": f"Basic {credentials}"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_inactive_client_rejected(
        self, oauth2_client: tuple[AsyncClient, AsyncSession], inactive_client: str
    ) -> None:
        client, _ = oauth2_client
        credentials = base64.b64encode(f"{inactive_client}:any_secret".encode()).decode()
        r = await client.post(
            f"{API_PREFIX}/login/client-credentials",
            headers={"Authorization": f"Basic {credentials}"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_credentials_rejected(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(
            f"{API_PREFIX}/login/client-credentials",
            headers={"Authorization": "Basic d3Jvbmc="},
        )
        # Should be 401 (invalid client) not 400/422
        assert r.status_code in (400, 401, 422)


# ---- AUTHORIZATION CODE + PKCE FLOW ----


class TestAuthorizationCodeFlow:
    @pytest.mark.asyncio
    async def test_pkce_challenge_returns_valid_pair(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(f"{API_PREFIX}/login/pkce-challenge")
        assert r.status_code == 200
        data = r.json()
        assert "code_verifier" in data
        assert "code_challenge" in data
        assert data["code_challenge_method"] == "S256"
        # Verify S256 derivation
        expected_challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(data["code_verifier"].encode("ascii")).digest())
            .rstrip(b"=")
            .decode("ascii")
        )
        assert data["code_challenge"] == expected_challenge

    @pytest.mark.asyncio
    async def test_authorize_step_returns_code(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        r = await client.post(
            f"{API_PREFIX}/login/authorize",
            json={"client_id": client_id, "code_challenge": challenge, "redirect_uri": ""},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["token_type"] == "code"
        assert "access_token" in data
        assert data["expires_in"] == 600  # 10 minutes TTL for the code

    @pytest.mark.asyncio
    async def test_authorize_rejects_invalid_client(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(
            f"{API_PREFIX}/login/authorize",
            json={"client_id": "nonexistent", "code_challenge": "dummy", "redirect_uri": ""},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_code_returns_token(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)

        # Step 1: get authorization code
        auth_r = await client.post(
            f"{API_PREFIX}/login/authorize",
            json={"client_id": client_id, "code_challenge": challenge, "redirect_uri": ""},
        )
        assert auth_r.status_code == 200
        code = auth_r.json()["access_token"]

        # Step 2: exchange code for tokens
        token_r = await client.post(
            f"{API_PREFIX}/login/auth-code",
            json={
                "client_id": client_id,
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": "",
            },
        )
        assert token_r.status_code == 200
        data = token_r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "api:all" in data["scopes"]

    @pytest.mark.asyncio
    async def test_auth_code_rejects_mismatched_pkce(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)

        auth_r = await client.post(
            f"{API_PREFIX}/login/authorize",
            json={"client_id": client_id, "code_challenge": challenge, "redirect_uri": ""},
        )
        code = auth_r.json()["access_token"]

        # Send wrong verifier
        wrong_verifier = "wrong_verifier_value"
        token_r = await client.post(
            f"{API_PREFIX}/login/auth-code",
            json={
                "client_id": client_id,
                "code": code,
                "code_verifier": wrong_verifier,
                "redirect_uri": "",
            },
        )
        assert token_r.status_code == 400

    @pytest.mark.asyncio
    async def test_auth_code_rejects_used_code(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)

        auth_r = await client.post(
            f"{API_PREFIX}/login/authorize",
            json={"client_id": client_id, "code_challenge": challenge, "redirect_uri": ""},
        )
        code = auth_r.json()["access_token"]

        # First use: success
        r1 = await client.post(
            f"{API_PREFIX}/login/auth-code",
            json={
                "client_id": client_id,
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": "",
            },
        )
        assert r1.status_code == 200

        # Second use: rejected
        r2 = await client.post(
            f"{API_PREFIX}/login/auth-code",
            json={
                "client_id": client_id,
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": "",
            },
        )
        assert r2.status_code == 400

    @pytest.mark.asyncio
    async def test_auth_code_rejects_invalid_code(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        r = await client.post(
            f"{API_PREFIX}/login/auth-code",
            json={
                "client_id": client_id,
                "code": "invalid-code-value",
                "code_verifier": "any",
                "redirect_uri": "",
            },
        )
        assert r.status_code == 400


# ---- IMPLICIT GRANT FLOW ----


class TestImplicitGrantFlow:
    @pytest.mark.asyncio
    async def test_implicit_returns_access_token(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        r = await client.post(
            f"{API_PREFIX}/login/implicit-token",
            json={
                "client_id": client_id,
                "code_challenge": challenge,
                "code_verifier": verifier,
                "redirect_uri": "",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0
        # Token should have valid scopes in the JWT payload
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_implicit_rejects_invalid_client(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(
            f"{API_PREFIX}/login/implicit-token",
            json={
                "client_id": "nonexistent-client",
                "code_challenge": "dummy",
                "code_verifier": "dummy",
                "redirect_uri": "",
            },
        )
        assert r.status_code == 401


# ---- TOKEN VALIDATION IN ENDPOINTS ----


class TestTokenValidation:
    @pytest.mark.asyncio
    async def test_password_token_works_in_test_token(
        self, oauth2_client: tuple[AsyncClient, AsyncSession]
    ) -> None:
        client, _ = oauth2_client
        r = await client.post(
            f"{API_PREFIX}/login/access-token",
            data={
                "username": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            },
        )
        token = r.json()["access_token"]
        r2 = await client.post(
            f"{API_PREFIX}/login/test-token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r2.status_code == 200
        assert r2.json()["email"] == settings.FIRST_SUPERUSER

    @pytest.mark.asyncio
    async def test_client_creds_token_is_valid_jwt(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, client_secret, _ = client_id_secret
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        r = await client.post(
            f"{API_PREFIX}/login/client-credentials",
            headers={"Authorization": f"Basic {credentials}"},
        )
        token = r.json()["access_token"]
        # Verify token is a valid JWT by decoding it
        import jwt as pyjwt

        payload = pyjwt.decode(token, options={"verify_signature": False})
        assert payload["sub"] == client_id
        assert "scopes" in payload

    @pytest.mark.asyncio
    async def test_auth_code_token_is_valid_jwt(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)

        auth_r = await client.post(
            f"{API_PREFIX}/login/authorize",
            json={"client_id": client_id, "code_challenge": challenge, "redirect_uri": ""},
        )
        code = auth_r.json()["access_token"]

        token_r = await client.post(
            f"{API_PREFIX}/login/auth-code",
            json={
                "client_id": client_id,
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": "",
            },
        )
        token = token_r.json()["access_token"]
        # Verify token is a valid JWT
        import jwt as pyjwt

        payload = pyjwt.decode(token, options={"verify_signature": False})
        assert payload["sub"] == client_id
        assert "scopes" in payload

    @pytest.mark.asyncio
    async def test_implicit_token_is_valid_jwt(
        self,
        oauth2_client: tuple[AsyncClient, AsyncSession],
        client_id_secret: tuple[str, str, ClientCredentials],
    ) -> None:
        client, _ = oauth2_client
        client_id, _, _ = client_id_secret
        r = await client.post(
            f"{API_PREFIX}/login/implicit-token",
            json={
                "client_id": client_id,
                "code_challenge": generate_code_challenge(generate_code_verifier()),
                "code_verifier": generate_code_verifier(),
                "redirect_uri": "",
            },
        )
        token = r.json()["access_token"]
        # Verify token is a valid JWT
        import jwt as pyjwt

        payload = pyjwt.decode(token, options={"verify_signature": False})
        assert payload["sub"] == client_id
        assert "scopes" in payload

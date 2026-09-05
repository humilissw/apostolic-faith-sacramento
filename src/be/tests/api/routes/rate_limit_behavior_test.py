"""Behavioral tests for login rate limiting.

Guards the fix: successful logins must NEVER consume the login rate-limit
budget; only failed credential attempts count, and a later success clears it.
"""

import httpx
import pytest
from httpx import ASGITransport

from app.config import settings
from app.core.rate_limiter import (
    LOGIN_MAX_ATTEMPTS,
    check_rate_limit,
    login_bucket_key,
    reset_rate_limit,
)
from app.crud import create_user
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string

LOGIN_URL = None  # resolved from settings at call time


@pytest.fixture(autouse=True)
def _reset_rl():
    reset_rate_limit()
    yield
    reset_rate_limit()


@pytest.fixture(scope="function")
async def rl_client() -> httpx.AsyncClient:  # type: ignore[valid-type]
    from app.main import app

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


def _login_url() -> str:
    return f"{settings.API_V1_STR}/login/access-token"


async def _attempt(client: httpx.AsyncClient, username: str, password: str) -> httpx.Response:
    return await client.post(
        _login_url(), data={"username": username, "password": password}
    )


async def test_repeated_failed_logins_lock_out_after_max_attempts(rl_client):
    """Brute-force protection still works: N failures -> 429 on attempt N+1."""
    for i in range(LOGIN_MAX_ATTEMPTS):
        resp = await _attempt(rl_client, "nobody@example.com", "wrong")
        assert resp.status_code == 400, f"attempt {i}: expected 400, got {resp.status_code}"

    resp = await _attempt(rl_client, "nobody@example.com", "wrong")
    assert resp.status_code == 429
    assert int(resp.headers["retry-after"]) > 0


async def test_successful_logins_never_trigger_rate_limit(rl_client, db_session):
    """A legitimate user logging in repeatedly must never be locked out."""
    email = random_email()
    password = random_lower_string()
    await create_user(
        session=db_session,
        user_create=UserCreate(email=email, password=password, is_active=True),
    )

    for i in range(LOGIN_MAX_ATTEMPTS + 10):
        resp = await _attempt(rl_client, email, password)
        assert resp.status_code == 200, f"login {i}: got {resp.status_code} {resp.text}"


async def test_success_after_failures_clears_lockout(rl_client, db_session):
    """Failed attempts burn slots, but a successful login resets the bucket."""
    email = random_email()
    password = random_lower_string()
    await create_user(
        session=db_session,
        user_create=UserCreate(email=email, password=password, is_active=True),
    )

    for _ in range(LOGIN_MAX_ATTEMPTS - 1):
        resp = await _attempt(rl_client, email, "wrong")
        assert resp.status_code == 400

    # User finally types the right password — must succeed and reset bucket.
    resp = await _attempt(rl_client, email, password)
    assert resp.status_code == 200

    key = login_bucket_key("127.0.0.1")
    assert check_rate_limit(key, LOGIN_MAX_ATTEMPTS, 15 * 60, consume=False) is True

    # And the full budget is available again for future failures.
    for i in range(LOGIN_MAX_ATTEMPTS - 1):
        resp = await _attempt(rl_client, email, "wrong")
        assert resp.status_code == 400, f"post-reset attempt {i}: {resp.status_code}"


async def test_middleware_enforces_lockout_without_consuming(rl_client):
    """Middleware rejects locked-out clients but never adds to the bucket."""
    key = login_bucket_key("127.0.0.1")
    # Pre-fill the bucket directly (simulating failed attempts).
    for _ in range(LOGIN_MAX_ATTEMPTS):
        assert check_rate_limit(key, LOGIN_MAX_ATTEMPTS, 15 * 60) is True

    resp = await _attempt(rl_client, "nobody@example.com", "whatever")
    assert resp.status_code == 429


async def test_xff_header_gives_distinct_buckets(rl_client):
    """Two clients behind one proxy IP must not share a login bucket."""
    for i in range(LOGIN_MAX_ATTEMPTS):
        for ip in ("203.0.113.1", "203.0.113.2"):
            resp = await rl_client.post(
                _login_url(),
                data={"username": "nobody@example.com", "password": "wrong"},
                headers={"X-Forwarded-For": ip},
            )
            assert resp.status_code == 400, f"{ip} attempt {i}: {resp.status_code}"

    # Both are now locked out...
    for ip in ("203.0.113.1", "203.0.113.2"):
        resp = await rl_client.post(
            _login_url(),
            data={"username": "nobody@example.com", "password": "wrong"},
            headers={"X-Forwarded-For": ip},
        )
        assert resp.status_code == 429

    # ...but a third client behind the same proxy is unaffected.
    resp = await rl_client.post(
        _login_url(),
        data={"username": "nobody@example.com", "password": "wrong"},
        headers={"X-Forwarded-For": "203.0.113.3"},
    )
    assert resp.status_code == 400

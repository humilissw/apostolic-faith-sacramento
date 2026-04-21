import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_utils_health_check(client) -> None:
    response = await client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


@pytest.mark.asyncio
async def test_test_email_success(client, superuser_token_headers) -> None:
    test_email = "test@example.com"
    with patch("app.api.routes.utils.send_email", return_value=None):
        response = await client.post(
            "/api/v1/utils/test-email/",
            headers=superuser_token_headers,
            params={"email_to": test_email},
        )
    assert response.status_code == 201
    assert response.json()["message"] == "Test email sent"


@pytest.mark.asyncio
async def test_test_email_not_superuser(client) -> None:
    test_email = "test@example.com"
    response = await client.post(
        "/api/v1/utils/test-email/",
        json={"email_to": test_email},
    )
    assert response.status_code == 401

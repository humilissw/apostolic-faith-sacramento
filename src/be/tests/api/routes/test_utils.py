import pytest
from pydantic.networks import EmailStr


def test_utils_health_check(client) -> None:
    """Test utils health check endpoint."""
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


def test_test_email_success(client, superuser_token_headers) -> None:
    """Test sending test email."""
    test_email = "test@example.com"
    response = client.post(
        "/api/v1/utils/test-email/",
        headers=superuser_token_headers,
        json={"email_to": test_email},
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Test email sent"


def test_test_email_not_superuser(client) -> None:
    """Test that test email requires superuser."""
    test_email = "test@example.com"
    response = client.post(
        "/api/v1/utils/test-email/",
        json={"email_to": test_email},
    )
    # Should get 401 Unauthorized (default for non-authenticated)
    assert response.status_code == 401
import pytest


def test_members_health_check(client) -> None:
    """Test members health check endpoint."""
    response = client.get("/api/v1/members/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


def test_members_liveness(client) -> None:
    """Test members liveness probe."""
    response = client.get("/api/v1/members/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


def test_members_readiness(client) -> None:
    """Test members readiness probe."""
    response = client.get("/api/v1/members/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"
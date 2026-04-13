import pytest


def test_announcements_health_check(client) -> None:
    """Test announcements health check endpoint."""
    response = client.get("/api/v1/announcements/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


def test_announcements_liveness(client) -> None:
    """Test announcements liveness probe."""
    response = client.get("/api/v1/announcements/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


def test_announcements_readiness(client) -> None:
    """Test announcements readiness probe."""
    response = client.get("/api/v1/announcements/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"
import pytest


def test_church_services_health_check(client) -> None:
    """Test church services health check endpoint."""
    response = client.get("/api/v1/church-services/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


def test_church_services_liveness(client) -> None:
    """Test church services liveness probe."""
    response = client.get("/api/v1/church-services/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


def test_church_services_readiness(client) -> None:
    """Test church services readiness probe."""
    response = client.get("/api/v1/church-services/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"
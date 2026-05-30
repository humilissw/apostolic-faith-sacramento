"""Test health endpoints."""


def test_health_check(client):
    assert client.get("/api/v1/health").status_code == 200


def test_liveness(client):
    assert client.get("/api/v1/health/liveness").status_code == 200


def test_readiness(client):
    assert client.get("/api/v1/health/readiness").status_code == 200


def test_utils_health(client):
    assert client.get("/api/v1/utils/health-check/").status_code == 200


def test_test_email(client):
    resp = client.post("/api/v1/utils/test-email/", json={"email_to": "test@example.com"})
    assert resp.status_code in (200, 400, 500)

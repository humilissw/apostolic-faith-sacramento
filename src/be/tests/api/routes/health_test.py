import pytest


@pytest.mark.asyncio
async def test_get_health(client) -> None:
    response = await client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


@pytest.mark.asyncio
async def test_get_liveness(client) -> None:
    response = await client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


@pytest.mark.asyncio
async def test_get_readiness(client) -> None:
    response = await client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"

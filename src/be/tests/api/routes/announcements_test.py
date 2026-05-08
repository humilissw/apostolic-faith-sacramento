import pytest


@pytest.mark.asyncio
async def test_announcements_health_check(client) -> None:
    response = await client.get("/api/v1/announcements/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


@pytest.mark.asyncio
async def test_announcements_liveness(client) -> None:
    response = await client.get("/api/v1/announcements/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


@pytest.mark.asyncio
async def test_announcements_readiness(client) -> None:
    response = await client.get("/api/v1/announcements/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"

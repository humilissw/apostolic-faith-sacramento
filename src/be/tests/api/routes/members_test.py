import pytest


@pytest.mark.asyncio
async def test_members_health_check(client) -> None:
    response = await client.get("/api/v1/members/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


@pytest.mark.asyncio
async def test_members_liveness(client) -> None:
    response = await client.get("/api/v1/members/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


@pytest.mark.asyncio
async def test_members_readiness(client) -> None:
    response = await client.get("/api/v1/members/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"

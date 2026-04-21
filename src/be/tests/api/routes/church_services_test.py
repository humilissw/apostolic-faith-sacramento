import pytest


@pytest.mark.asyncio
async def test_church_services_health_check(client) -> None:
    response = await client.get("/api/v1/church-services/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


@pytest.mark.asyncio
async def test_church_services_liveness(client) -> None:
    response = await client.get("/api/v1/church-services/liveness")
    assert response.status_code == 200
    assert response.json() == "Live"


@pytest.mark.asyncio
async def test_church_services_readiness(client) -> None:
    response = await client.get("/api/v1/church-services/readiness")
    assert response.status_code == 200
    assert response.json() == "Ready"

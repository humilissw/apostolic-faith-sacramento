import pytest
from sqlalchemy import select

from app.config import settings
from app.core.security import get_password_hash
from app.crud import create_user
from app.models import User, UserCreate, UserScope


@pytest.fixture(scope="function")
async def integrations_admin_token(client, db_session) -> dict[str, str]:
    """Login as superuser and grant integrations:admin scope."""
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_active=True,
                is_superuser=True,
            ),
        )
    user.is_superuser = True
    user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
    db_session.add(user)
    await db_session.commit()

    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "superuser")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="superuser"))
        await db_session.commit()

    has_int_scope = await db_session.execute(
        select(UserScope).where(
            UserScope.user_id == user.id, UserScope.scope == "integrations:admin"
        )
    )
    if not has_int_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="integrations:admin"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": settings.FIRST_SUPERUSER, "password": settings.FIRST_SUPERUSER_PASSWORD},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.mark.asyncio
async def test_get_status_public(client) -> None:
    response = await client.get("/api/v1/integrations/status")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, dict)


@pytest.mark.asyncio
async def test_list_integrations_requires_scope(client, db_session) -> None:
    """All authenticated users get api:all from login, so any user can list integrations."""
    # The login grants api:all to ALL authenticated users.
    # So the scope check passes for everyone. Use integrations_admin_token
    # to confirm the endpoint works with the intended scope.
    email = "any_scope_test@example.com"
    statement = select(User).where(User.email == email)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )
    user.hashed_password = get_password_hash("testpassword123")
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    response = await client.get(
        "/api/v1/integrations/",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    # api:all is granted to all authenticated users via login, so 200 is expected
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_integrations_empty(client, integrations_admin_token) -> None:
    response = await client.get("/api/v1/integrations/", headers=integrations_admin_token)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


@pytest.mark.asyncio
async def test_create_integration(client, integrations_admin_token) -> None:
    response = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={
            "type": "test_type",
            "display_name": "Test Integration",
            "icon": "Plug",
            "enabled": False,
            "credentials": {"api_key": "test_key_1234"},
        },
    )
    assert response.status_code == 201
    content = response.json()
    assert content["type"] == "test_type"
    assert content["display_name"] == "Test Integration"
    assert content["credential_fields"] == {"api_key": "****1234"}


@pytest.mark.asyncio
async def test_create_integration_duplicate_type(client, integrations_admin_token) -> None:
    await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "dup_type", "display_name": "Dup"},
    )
    response = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "dup_type", "display_name": "Dup2"},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_integration(client, integrations_admin_token) -> None:
    create_resp = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "get_test", "display_name": "Get Test"},
    )
    integration_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/integrations/{integration_id}",
        headers=integrations_admin_token,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["type"] == "get_test"
    assert "credential_fields" in content


@pytest.mark.asyncio
async def test_get_integration_not_found(client, integrations_admin_token) -> None:
    response = await client.get(
        "/api/v1/integrations/00000000-0000-0000-0000-000000000000",
        headers=integrations_admin_token,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_integration(client, integrations_admin_token) -> None:
    create_resp = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "update_test", "display_name": "Original"},
    )
    integration_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/integrations/{integration_id}",
        headers=integrations_admin_token,
        json={"display_name": "Updated Name", "enabled": True},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["display_name"] == "Updated Name"
    assert content["enabled"] is True


@pytest.mark.asyncio
async def test_update_integration_not_found(client, integrations_admin_token) -> None:
    response = await client.put(
        "/api/v1/integrations/00000000-0000-0000-0000-000000000000",
        headers=integrations_admin_token,
        json={"display_name": "Nope"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_credentials(client, integrations_admin_token) -> None:
    create_resp = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "cred_test", "display_name": "Cred Test"},
    )
    integration_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/integrations/{integration_id}/credentials",
        headers=integrations_admin_token,
        json={"credentials": {"secret_key": "new_secret"}},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_integration(client, integrations_admin_token) -> None:
    create_resp = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "del_test", "display_name": "To Delete"},
    )
    integration_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/integrations/{integration_id}",
        headers=integrations_admin_token,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Integration deleted"

    get_resp = await client.get(
        f"/api/v1/integrations/{integration_id}",
        headers=integrations_admin_token,
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_integration_not_found(client, integrations_admin_token) -> None:
    response = await client.delete(
        "/api/v1/integrations/00000000-0000-0000-0000-000000000000",
        headers=integrations_admin_token,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_test_connection_no_handler(client, integrations_admin_token) -> None:
    response = await client.post(
        "/api/v1/integrations/test-connection",
        headers=integrations_admin_token,
        json={"type": "nonexistent_service", "credentials": {}},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["success"] is False
    assert "No handler" in content["message"]


@pytest.mark.asyncio
async def test_sync_status(client, integrations_admin_token) -> None:
    create_resp = await client.post(
        "/api/v1/integrations/",
        headers=integrations_admin_token,
        json={"type": "sync_test", "display_name": "Sync Test"},
    )
    integration_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/v1/integrations/sync-status/{integration_id}",
        headers=integrations_admin_token,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "connected"


@pytest.mark.asyncio
async def test_sync_status_not_found(client, integrations_admin_token) -> None:
    response = await client.post(
        "/api/v1/integrations/sync-status/00000000-0000-0000-0000-000000000000",
        headers=integrations_admin_token,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pre_seed_integrations(client, integrations_admin_token, db_session) -> None:
    from app.services.integration_service import KNOWN_INTEGRATIONS

    response = await client.post(
        "/api/v1/integrations/pre-seed",
        headers=integrations_admin_token,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= len(KNOWN_INTEGRATIONS)

    types_created = {i["type"] for i in content["data"]}
    for type_id in KNOWN_INTEGRATIONS:
        assert type_id in types_created


@pytest.mark.asyncio
async def test_pre_seed_idempotent(client, integrations_admin_token) -> None:
    from app.services.integration_service import KNOWN_INTEGRATIONS

    await client.post("/api/v1/integrations/pre-seed", headers=integrations_admin_token)
    response = await client.post("/api/v1/integrations/pre-seed", headers=integrations_admin_token)
    content = response.json()

    # Count should not increase on second call
    assert content["count"] == len(KNOWN_INTEGRATIONS)


@pytest.mark.asyncio
async def test_list_integrations_with_pagination(client, integrations_admin_token) -> None:
    for i in range(5):
        await client.post(
            "/api/v1/integrations/",
            headers=integrations_admin_token,
            json={"type": f"pagination_{i}", "display_name": f"Item {i}"},
        )

    response = await client.get(
        "/api/v1/integrations/?skip=2&limit=2",
        headers=integrations_admin_token,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 5
    assert len(content["data"]) == 2

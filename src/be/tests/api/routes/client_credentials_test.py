import pytest


@pytest.mark.asyncio
async def test_list_client_credentials_empty(client, superuser_token_headers) -> None:
    response = await client.get(
        "/api/v1/admin/client-credentials/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) == 0


@pytest.mark.asyncio
async def test_list_client_credentials_forbidden(client, normal_user_token_headers) -> None:
    response = await client.get(
        "/api/v1/admin/client-credentials/", headers=normal_user_token_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_client_credentials(client, superuser_token_headers) -> None:
    import uuid

    test_client_id = f"test_client_{uuid.uuid4().hex}"
    response = await client.post(
        "/api/v1/admin/client-credentials/",
        headers=superuser_token_headers,
        json={"client_id": test_client_id, "scopes": ["payments:read", "payments:write"]},
    )
    assert response.status_code == 201
    content = response.json()
    assert content["client_id"] == test_client_id
    assert content["is_active"] is True
    assert set(content["scopes"]) == {"payments:read", "payments:write"}


@pytest.mark.asyncio
async def test_create_client_credentials_duplicate(client, superuser_token_headers) -> None:
    import uuid

    test_client_id = f"dup_client_{uuid.uuid4().hex}"
    await client.post(
        "/api/v1/admin/client-credentials/",
        headers=superuser_token_headers,
        json={"client_id": test_client_id, "scopes": ["read"]},
    )
    response = await client.post(
        "/api/v1/admin/client-credentials/",
        headers=superuser_token_headers,
        json={"client_id": test_client_id, "scopes": ["write"]},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_client_credentials(client, superuser_token_headers) -> None:
    import uuid

    create_resp = await client.post(
        "/api/v1/admin/client-credentials/",
        headers=superuser_token_headers,
        json={"client_id": f"update_test_{uuid.uuid4().hex}", "scopes": ["read"]},
    )
    cc_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/admin/client-credentials/{cc_id}",
        headers=superuser_token_headers,
        json={"scopes": ["read", "write", "delete"], "is_active": False},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_active"] is False
    assert set(content["scopes"]) == {"read", "write", "delete"}


@pytest.mark.asyncio
async def test_update_client_credentials_not_found(client, superuser_token_headers) -> None:
    response = await client.patch(
        "/api/v1/admin/client-credentials/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
        json={"is_active": False},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_client_credentials(client, superuser_token_headers) -> None:
    import uuid

    create_resp = await client.post(
        "/api/v1/admin/client-credentials/",
        headers=superuser_token_headers,
        json={"client_id": f"delete_test_{uuid.uuid4().hex}", "scopes": ["read"]},
    )
    cc_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/admin/client-credentials/{cc_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_client_credentials_not_found(client, superuser_token_headers) -> None:
    response = await client.delete(
        "/api/v1/admin/client-credentials/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404

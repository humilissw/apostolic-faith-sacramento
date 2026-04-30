import pytest


@pytest.mark.asyncio
async def test_read_media_empty(client, superuser_token_headers) -> None:
    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


@pytest.mark.asyncio
async def test_create_media(client, superuser_token_headers) -> None:
    response = await client.post(
        "/api/v1/media/",
        headers=superuser_token_headers,
        json={"name": "Test Media"},
    )
    assert response.status_code == 201
    content = response.json()
    assert content["id"] is not None
    assert content["name"] == "Test Media"
    assert content["uploaded_on"] is not None
    assert content["created_on"] is not None
    assert content["updated_on"] is not None


@pytest.mark.asyncio
async def test_read_media(client, superuser_token_headers) -> None:
    await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "First Media"}
    )
    await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "Second Media"}
    )

    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2
    media_names = [media["name"] for media in content["data"]]
    assert "First Media" in media_names
    assert "Second Media" in media_names


@pytest.mark.asyncio
async def test_read_media_by_id(client, superuser_token_headers) -> None:
    create_response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "Unique Media"}
    )
    media_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == media_id
    assert content["name"] == "Unique Media"
    assert content["uploaded_on"] is not None


@pytest.mark.asyncio
async def test_read_media_by_id_not_found(client, superuser_token_headers) -> None:
    response = await client.get(
        "/api/v1/media/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_media(client, superuser_token_headers) -> None:
    create_response = await client.post(
        "/api/v1/media/",
        headers=superuser_token_headers,
        json={"name": "Original Name"},
    )
    media_id = create_response.json()["id"]

    update_data = {"name": "Updated Name"}
    response = await client.patch(
        f"/api/v1/media/{media_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == "Updated Name"
    assert content["updated_on"] is not None


@pytest.mark.asyncio
async def test_update_media_not_found(client, superuser_token_headers) -> None:
    response = await client.patch(
        "/api/v1/media/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
        json={"name": "Updated Name"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_media(client, superuser_token_headers) -> None:
    create_response = await client.post(
        "/api/v1/media/",
        headers=superuser_token_headers,
        json={"name": "To Be Deleted"},
    )
    media_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Media deleted successfully"

    get_response = await client.get(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_media_not_found(client, superuser_token_headers) -> None:
    response = await client.delete(
        "/api/v1/media/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination(client, superuser_token_headers) -> None:
    for i in range(10):
        await client.post(
            "/api/v1/media/",
            headers=superuser_token_headers,
            json={"name": f"Media {i}"},
        )

    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 10

    response = await client.get("/api/v1/media/?skip=5&limit=3", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 3

    response = await client.get("/api/v1/media/?limit=2", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 2


@pytest.mark.asyncio
async def test_media_duplicate_names(client, superuser_token_headers) -> None:
    await client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Same Name"})
    await client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Same Name"})

    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    for media in content["data"]:
        assert media["name"] == "Same Name"


@pytest.mark.asyncio
async def test_media_validation(client, superuser_token_headers) -> None:
    long_name = "a" * 201
    response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": long_name}
    )
    assert response.status_code == 422

    response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": ""}
    )
    assert response.status_code == 201

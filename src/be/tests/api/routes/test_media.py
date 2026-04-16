import uuid

import pytest
from httpx import AsyncClient

from tests.utils.item import create_random_item


async def test_read_media_empty(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test reading media when the database is empty."""
    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


async def test_create_media(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test creating a new media entry."""
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


async def test_read_media(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test reading all media entries."""
    # Create some media entries
    await client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "First Media"})
    await client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Second Media"})

    # Read all media
    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2
    media_names = [media["name"] for media in content["data"]]
    assert "First Media" in media_names
    assert "Second Media" in media_names


async def test_read_media_by_id(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test reading a single media entry by ID."""
    # Create a media entry
    create_response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "Unique Media"}
    )
    media_id = create_response.json()["id"]

    # Read by ID
    response = await client.get(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == media_id
    assert content["name"] == "Unique Media"
    assert content["uploaded_on"] is not None


async def test_read_media_by_id_not_found(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test reading a non-existent media entry."""
    response = await client.get("/api/v1/media/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_update_media(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test updating a media entry."""
    # Create a media entry
    create_response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "Original Name"}
    )
    media_id = create_response.json()["id"]

    # Update the media entry
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


async def test_update_media_not_found(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test updating a non-existent media entry."""
    response = await client.patch(
        "/api/v1/media/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
        json={"name": "Updated Name"},
    )
    assert response.status_code == 404


async def test_delete_media(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test deleting a media entry."""
    # Create a media entry
    create_response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "To Be Deleted"}
    )
    media_id = create_response.json()["id"]

    # Delete the media entry
    response = await client.delete(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Media deleted successfully"

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert get_response.status_code == 404


async def test_delete_media_not_found(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test deleting a non-existent media entry."""
    response = await client.delete("/api/v1/media/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers)
    assert response.status_code == 404


async def test_pagination(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test pagination of media entries."""
    # Create 10 media entries
    for i in range(10):
        await client.post(
            "/api/v1/media/", headers=superuser_token_headers, json={"name": f"Media {i}"}
        )

    # Test default limit
    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 10

    # Test with skip
    response = await client.get("/api/v1/media/?skip=5&limit=3", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 3

    # Test with limit less than total
    response = await client.get("/api/v1/media/?limit=2", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 2


async def test_media_duplicate_names(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test creating media entries with the same name."""
    # Create two entries with the same name
    await client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Same Name"})
    await client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Same Name"})

    # Read all media
    response = await client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    # All entries should have the same name
    for media in content["data"]:
        assert media["name"] == "Same Name"


async def test_media_validation(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    """Test validation for media creation."""
    # Test name too long
    long_name = "a" * 201
    response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": long_name}
    )
    assert response.status_code == 422  # Validation error

    # Test empty name is allowed
    response = await client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": ""}
    )
    assert response.status_code == 201
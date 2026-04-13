import uuid

import pytest
from sqlmodel import Session

from tests.utils.item import create_random_item


def test_read_media_empty(client, superuser_token_headers) -> None:
    """Test reading media when the database is empty."""
    response = client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


def test_create_media(client, superuser_token_headers, db: Session) -> None:
    """Test creating a new media entry."""
    response = client.post(
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


def test_read_media(client, superuser_token_headers, db: Session) -> None:
    """Test reading all media entries."""
    # Create some media entries
    client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "First Media"})
    client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Second Media"})

    # Read all media
    response = client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2
    media_names = [media["name"] for media in content["data"]]
    assert "First Media" in media_names
    assert "Second Media" in media_names


def test_read_media_by_id(client, superuser_token_headers, db: Session) -> None:
    """Test reading a single media entry by ID."""
    # Create a media entry
    create_response = client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "Unique Media"}
    )
    media_id = create_response.json()["id"]

    # Read by ID
    response = client.get(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == media_id
    assert content["name"] == "Unique Media"
    assert content["uploaded_on"] is not None


def test_read_media_by_id_not_found(client, superuser_token_headers) -> None:
    """Test reading a non-existent media entry."""
    response = client.get("/api/v1/media/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_media(client, superuser_token_headers, db: Session) -> None:
    """Test updating a media entry."""
    # Create a media entry
    create_response = client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "Original Name"}
    )
    media_id = create_response.json()["id"]

    # Update the media entry
    update_data = {"name": "Updated Name"}
    response = client.patch(
        f"/api/v1/media/{media_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == "Updated Name"
    assert content["updated_on"] is not None


def test_update_media_not_found(client, superuser_token_headers) -> None:
    """Test updating a non-existent media entry."""
    response = client.patch(
        "/api/v1/media/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
        json={"name": "Updated Name"},
    )
    assert response.status_code == 404


def test_delete_media(client, superuser_token_headers, db: Session) -> None:
    """Test deleting a media entry."""
    # Create a media entry
    create_response = client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "To Be Deleted"}
    )
    media_id = create_response.json()["id"]

    # Delete the media entry
    response = client.delete(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Media deleted successfully"

    # Verify it's deleted
    get_response = client.get(f"/api/v1/media/{media_id}", headers=superuser_token_headers)
    assert get_response.status_code == 404


def test_delete_media_not_found(client, superuser_token_headers) -> None:
    """Test deleting a non-existent media entry."""
    response = client.delete("/api/v1/media/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers)
    assert response.status_code == 404


def test_pagination(client, superuser_token_headers, db: Session) -> None:
    """Test pagination of media entries."""
    # Create 10 media entries
    for i in range(10):
        client.post(
            "/api/v1/media/", headers=superuser_token_headers, json={"name": f"Media {i}"}
        )

    # Test default limit
    response = client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 10

    # Test with skip
    response = client.get("/api/v1/media/?skip=5&limit=3", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 3

    # Test with limit less than total
    response = client.get("/api/v1/media/?limit=2", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 2


def test_media_duplicate_names(client, superuser_token_headers, db: Session) -> None:
    """Test creating media entries with the same name."""
    # Create two entries with the same name
    client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Same Name"})
    client.post("/api/v1/media/", headers=superuser_token_headers, json={"name": "Same Name"})

    # Read all media
    response = client.get("/api/v1/media/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 2
    # All entries should have the same name
    for media in content["data"]:
        assert media["name"] == "Same Name"


def test_media_validation(client, superuser_token_headers) -> None:
    """Test validation for media creation."""
    # Test missing name
    response = client.post("/api/v1/media/", headers=superuser_token_headers, json={})
    assert response.status_code == 422  # Validation error

    # Test name too short
    response = client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": "ab"}
    )
    assert response.status_code == 422  # Validation error

    # Test name too long
    long_name = "a" * 201
    response = client.post(
        "/api/v1/media/", headers=superuser_token_headers, json={"name": long_name}
    )
    assert response.status_code == 422  # Validation error
import pytest
from fastapi.testclient import TestClient

from app.models import Media


class TestMediaRoutes:
    """Test suite for media API routes."""

    async def test_read_media_empty(self, client: TestClient, db_session):
        """Test reading media when the database is empty."""
        response = client.get("/media/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["data"] == []

    async def test_create_media(self, client: TestClient, db_session):
        """Test creating a new media entry."""
        response = client.post(
            "/media/",
            json={"name": "Test Media"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "Test Media"
        assert data["uploaded_on"] is not None
        assert data["created_on"] is not None
        assert data["updated_on"] is not None

    async def test_read_media(self, client: TestClient, db_session):
        """Test reading all media entries."""
        # Create a media entry
        client.post("/media/", json={"name": "First Media"})

        # Create another media entry
        client.post("/media/", json={"name": "Second Media"})

        # Read all media
        response = client.get("/media/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] in ["First Media", "Second Media"]
        assert data["data"][1]["name"] in ["First Media", "Second Media"]

    async def test_read_media_by_id(self, client: TestClient, db_session):
        """Test reading a single media entry by ID."""
        # Create a media entry
        create_response = client.post("/media/", json={"name": "Unique Media"})
        media_id = create_response.json()["id"]

        # Read by ID
        response = client.get(f"/media/{media_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == media_id
        assert data["name"] == "Unique Media"
        assert data["uploaded_on"] is not None

    async def test_read_media_by_id_not_found(self, client: TestClient, db_session):
        """Test reading a non-existent media entry."""
        response = client.get("/media/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_media(self, client: TestClient, db_session):
        """Test updating a media entry."""
        # Create a media entry
        create_response = client.post("/media/", json={"name": "Original Name"})
        media_id = create_response.json()["id"]

        # Update the media entry
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/media/{media_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["updated_on"] is not None

    async def test_update_media_not_found(self, client: TestClient, db_session):
        """Test updating a non-existent media entry."""
        response = client.patch(
            "/media/00000000-0000-0000-0000-000000000000",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 404

    async def test_delete_media(self, client: TestClient, db_session):
        """Test deleting a media entry."""
        # Create a media entry
        create_response = client.post("/media/", json={"name": "To Be Deleted"})
        media_id = create_response.json()["id"]

        # Delete the media entry
        response = client.delete(f"/media/{media_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Media deleted successfully"

        # Verify it's deleted
        get_response = client.get(f"/media/{media_id}")
        assert get_response.status_code == 404

    async def test_delete_media_not_found(self, client: TestClient, db_session):
        """Test deleting a non-existent media entry."""
        response = client.delete("/media/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_pagination(self, client: TestClient, db_session):
        """Test pagination of media entries."""
        # Create 10 media entries
        for i in range(10):
            client.post("/media/", json={"name": f"Media {i}"})

        # Test default limit
        response = client.get("/media/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["data"]) == 10

        # Test with skip
        response = client.get("/media/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["data"]) == 3

        # Test with limit less than total
        response = client.get("/media/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["data"]) == 2

    async def test_media_duplicate_names(self, client: TestClient, db_session):
        """Test creating media entries with the same name."""
        # Create two entries with the same name
        client.post("/media/", json={"name": "Same Name"})
        client.post("/media/", json={"name": "Same Name"})

        # Read all media
        response = client.get("/media/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        # All entries should have the same name
        for media in data["data"]:
            assert media["name"] == "Same Name"
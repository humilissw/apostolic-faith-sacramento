import pytest
from fastapi.testclient import TestClient

from app.models import VideoUpload


class TestVideoUploadRoutes:
    """Test suite for video upload API routes."""

    async def test_read_video_uploads_empty(self, client: TestClient, db_session):
        """Test reading video uploads when the database is empty."""
        response = client.get("/video-uploads/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["data"] == []

    async def test_create_video_upload(self, client: TestClient, db_session):
        """Test creating a new video upload entry."""
        response = client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/video.mp4",
                "upload_name": "test_video.mp4",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["upload_location"] == "s3://videos/bucket/path/to/video.mp4"
        assert data["upload_name"] == "test_video.mp4"
        assert data["created_on"] is not None
        assert data["updated_on"] is not None

    async def test_read_video_uploads(self, client: TestClient, db_session):
        """Test reading all video uploads."""
        # Create a video upload entry
        client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/video1.mp4",
                "upload_name": "video1.mp4",
            },
        )

        # Create another video upload entry
        client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/video2.mp4",
                "upload_name": "video2.mp4",
            },
        )

        # Read all video uploads
        response = client.get("/video-uploads/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["data"]) == 2
        assert data["data"][0]["upload_name"] in ["video1.mp4", "video2.mp4"]
        assert data["data"][1]["upload_name"] in ["video1.mp4", "video2.mp4"]

    async def test_read_video_upload_by_id(self, client: TestClient, db_session):
        """Test reading a single video upload by ID."""
        # Create a video upload entry
        create_response = client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/unique_video.mp4",
                "upload_name": "unique_video.mp4",
            },
        )
        video_upload_id = create_response.json()["id"]

        # Read by ID
        response = client.get(f"/video-uploads/{video_upload_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == video_upload_id
        assert data["upload_location"] == "s3://videos/bucket/path/to/unique_video.mp4"
        assert data["upload_name"] == "unique_video.mp4"

    async def test_read_video_upload_by_id_not_found(self, client: TestClient, db_session):
        """Test reading a non-existent video upload entry."""
        response = client.get("/video-uploads/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_update_video_upload(self, client: TestClient, db_session):
        """Test updating a video upload entry."""
        # Create a video upload entry
        create_response = client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/original.mp4",
                "upload_name": "original.mp4",
            },
        )
        video_upload_id = create_response.json()["id"]

        # Update the video upload entry
        update_data = {
            "upload_location": "s3://videos/bucket/path/to/updated.mp4",
            "upload_name": "updated.mp4",
        }
        response = client.patch(f"/video-uploads/{video_upload_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
        assert data["upload_name"] == "updated.mp4"
        assert data["updated_on"] is not None

    async def test_update_video_upload_not_found(self, client: TestClient, db_session):
        """Test updating a non-existent video upload entry."""
        response = client.patch(
            "/video-uploads/00000000-0000-0000-0000-000000000000",
            json={
                "upload_location": "s3://videos/bucket/path/to/updated.mp4",
                "upload_name": "updated.mp4",
            },
        )
        assert response.status_code == 404

    async def test_delete_video_upload(self, client: TestClient, db_session):
        """Test deleting a video upload entry."""
        # Create a video upload entry
        create_response = client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/delete_me.mp4",
                "upload_name": "delete_me.mp4",
            },
        )
        video_upload_id = create_response.json()["id"]

        # Delete the video upload entry
        response = client.delete(f"/video-uploads/{video_upload_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Video upload deleted successfully"

        # Verify it's deleted
        get_response = client.get(f"/video-uploads/{video_upload_id}")
        assert get_response.status_code == 404

    async def test_delete_video_upload_not_found(self, client: TestClient, db_session):
        """Test deleting a non-existent video upload entry."""
        response = client.delete("/video-uploads/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_pagination(self, client: TestClient, db_session):
        """Test pagination of video uploads."""
        # Create 10 video uploads
        for i in range(10):
            client.post(
                "/video-uploads/",
                json={
                    "upload_location": f"s3://videos/bucket/path/to/video{i}.mp4",
                    "upload_name": f"video{i}.mp4",
                },
            )

        # Test default limit
        response = client.get("/video-uploads/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["data"]) == 10

        # Test with skip
        response = client.get("/video-uploads/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["data"]) == 3

        # Test with limit less than total
        response = client.get("/video-uploads/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10
        assert len(data["data"]) == 2

    async def test_video_upload_validation(self, client: TestClient, db_session):
        """Test validation for video upload creation."""
        # Test missing fields
        response = client.post("/video-uploads/", json={})
        assert response.status_code == 422  # Validation error

        # Test missing upload_location
        response = client.post(
            "/video-uploads/",
            json={"upload_name": "test.mp4"},
        )
        assert response.status_code == 422

        # Test missing upload_name
        response = client.post(
            "/video-uploads/",
            json={"upload_location": "s3://videos/bucket/test.mp4"},
        )
        assert response.status_code == 422

        # Test upload_location too long
        long_location = "s3://videos/" + "a" * 1000 + ".mp4"
        response = client.post(
            "/video-uploads/",
            json={
                "upload_location": long_location,
                "upload_name": "test.mp4",
            },
        )
        assert response.status_code == 422  # Validation error

        # Test upload_name too long
        long_name = "a" * 1001
        response = client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/test.mp4",
                "upload_name": long_name,
            },
        )
        assert response.status_code == 422  # Validation error

    async def test_video_upload_update_partial_fields(self, client: TestClient, db_session):
        """Test updating only one field of a video upload."""
        # Create a video upload entry
        create_response = client.post(
            "/video-uploads/",
            json={
                "upload_location": "s3://videos/bucket/path/to/original.mp4",
                "upload_name": "original.mp4",
            },
        )
        video_upload_id = create_response.json()["id"]

        # Update only the upload_location
        response = client.patch(
            f"/video-uploads/{video_upload_id}",
            json={"upload_location": "s3://videos/bucket/path/to/updated.mp4"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
        assert data["upload_name"] == "original.mp4"  # Should remain the same

        # Update only the upload_name
        response = client.patch(
            f"/video-uploads/{video_upload_id}",
            json={"upload_name": "updated.mp4"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
        assert data["upload_name"] == "updated.mp4"  # Should be updated
import uuid

import pytest
from sqlmodel import Session


def test_read_video_uploads_empty(client, superuser_token_headers) -> None:
    """Test reading video uploads when the database is empty."""
    response = client.get("/api/v1/video-uploads/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


def test_create_video_upload(client, superuser_token_headers, db: Session) -> None:
    """Test creating a new video upload entry."""
    response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/video.mp4",
            "upload_name": "test_video.mp4",
        },
    )
    assert response.status_code == 201
    content = response.json()
    assert content["id"] is not None
    assert content["upload_location"] == "s3://videos/bucket/path/to/video.mp4"
    assert content["upload_name"] == "test_video.mp4"
    assert content["created_on"] is not None
    assert content["updated_on"] is not None


def test_read_video_uploads(client, superuser_token_headers, db: Session) -> None:
    """Test reading all video uploads."""
    # Create a video upload entry
    client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/video1.mp4",
            "upload_name": "video1.mp4",
        },
    )

    # Create another video upload entry
    client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/video2.mp4",
            "upload_name": "video2.mp4",
        },
    )

    # Read all video uploads
    response = client.get("/api/v1/video-uploads/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2
    video_names = [video["upload_name"] for video in content["data"]]
    assert "video1.mp4" in video_names
    assert "video2.mp4" in video_names


def test_read_video_upload_by_id(client, superuser_token_headers, db: Session) -> None:
    """Test reading a single video upload by ID."""
    # Create a video upload entry
    create_response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/unique_video.mp4",
            "upload_name": "unique_video.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]

    # Read by ID
    response = client.get(f"/api/v1/video-uploads/{video_upload_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == video_upload_id
    assert content["upload_location"] == "s3://videos/bucket/path/to/unique_video.mp4"
    assert content["upload_name"] == "unique_video.mp4"


def test_read_video_upload_by_id_not_found(client, superuser_token_headers) -> None:
    """Test reading a non-existent video upload entry."""
    response = client.get(
        "/api/v1/video-uploads/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_video_upload(client, superuser_token_headers, db: Session) -> None:
    """Test updating a video upload entry."""
    # Create a video upload entry
    create_response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
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
    response = client.patch(
        f"/api/v1/video-uploads/{video_upload_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
    assert content["upload_name"] == "updated.mp4"
    assert content["updated_on"] is not None


def test_update_video_upload_not_found(client, superuser_token_headers) -> None:
    """Test updating a non-existent video upload entry."""
    response = client.patch(
        "/api/v1/video-uploads/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/updated.mp4",
            "upload_name": "updated.mp4",
        },
    )
    assert response.status_code == 404


def test_delete_video_upload(client, superuser_token_headers, db: Session) -> None:
    """Test deleting a video upload entry."""
    # Create a video upload entry
    create_response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/delete_me.mp4",
            "upload_name": "delete_me.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]

    # Delete the video upload entry
    response = client.delete(
        f"/api/v1/video-uploads/{video_upload_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Video upload deleted successfully"

    # Verify it's deleted
    get_response = client.get(f"/api/v1/video-uploads/{video_upload_id}", headers=superuser_token_headers)
    assert get_response.status_code == 404


def test_delete_video_upload_not_found(client, superuser_token_headers) -> None:
    """Test deleting a non-existent video upload entry."""
    response = client.delete(
        "/api/v1/video-uploads/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers
    )
    assert response.status_code == 404


def test_pagination(client, superuser_token_headers, db: Session) -> None:
    """Test pagination of video uploads."""
    # Create 10 video uploads
    for i in range(10):
        client.post(
            "/api/v1/video-uploads/",
            headers=superuser_token_headers,
            json={
                "upload_location": f"s3://videos/bucket/path/to/video{i}.mp4",
                "upload_name": f"video{i}.mp4",
            },
        )

    # Test default limit
    response = client.get("/api/v1/video-uploads/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 10

    # Test with skip
    response = client.get("/api/v1/video-uploads/?skip=5&limit=3", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 3

    # Test with limit less than total
    response = client.get("/api/v1/video-uploads/?limit=2", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 2


def test_video_upload_validation(client, superuser_token_headers) -> None:
    """Test validation for video upload creation."""
    # Test missing fields
    response = client.post("/api/v1/video-uploads/", headers=superuser_token_headers, json={})
    assert response.status_code == 422  # Validation error

    # Test missing upload_location
    response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={"upload_name": "test.mp4"},
    )
    assert response.status_code == 422

    # Test missing upload_name
    response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={"upload_location": "s3://videos/bucket/test.mp4"},
    )
    assert response.status_code == 422

    # Test upload_location too long
    long_location = "s3://videos/" + "a" * 1000 + ".mp4"
    response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": long_location,
            "upload_name": "test.mp4",
        },
    )
    assert response.status_code == 422  # Validation error

    # Test upload_name too long
    long_name = "a" * 1001
    response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/test.mp4",
            "upload_name": long_name,
        },
    )
    assert response.status_code == 422  # Validation error


def test_video_upload_update_partial_fields(client, superuser_token_headers, db: Session) -> None:
    """Test updating only one field of a video upload."""
    # Create a video upload entry
    create_response = client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/original.mp4",
            "upload_name": "original.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]

    # Update only the upload_location
    response = client.patch(
        f"/api/v1/video-uploads/{video_upload_id}",
        headers=superuser_token_headers,
        json={"upload_location": "s3://videos/bucket/path/to/updated.mp4"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
    assert content["upload_name"] == "original.mp4"  # Should remain the same

    # Update only the upload_name
    response = client.patch(
        f"/api/v1/video-uploads/{video_upload_id}",
        headers=superuser_token_headers,
        json={"upload_name": "updated.mp4"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
    assert content["upload_name"] == "updated.mp4"  # Should be updated
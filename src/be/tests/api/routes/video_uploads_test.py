import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_read_video_uploads_empty(client, superuser_token_headers, db_session: AsyncSession) -> None:
    response = await client.get("/api/v1/video-uploads/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


@pytest.mark.asyncio
async def test_create_video_upload(client, superuser_token_headers, db_session: AsyncSession) -> None:
    response = await client.post(
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


@pytest.mark.asyncio
async def test_read_video_uploads(client, superuser_token_headers, db_session: AsyncSession) -> None:
    await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/video1.mp4",
            "upload_name": "video1.mp4",
        },
    )
    await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/video2.mp4",
            "upload_name": "video2.mp4",
        },
    )
    response = await client.get("/api/v1/video-uploads/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 2
    assert len(content["data"]) >= 2
    video_names = [video["upload_name"] for video in content["data"]]
    assert "video1.mp4" in video_names
    assert "video2.mp4" in video_names


@pytest.mark.asyncio
async def test_read_video_upload_by_id(client, superuser_token_headers, db_session: AsyncSession) -> None:
    create_response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/unique_video.mp4",
            "upload_name": "unique_video.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]
    response = await client.get(f"/api/v1/video-uploads/{video_upload_id}", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == video_upload_id
    assert content["upload_location"] == "s3://videos/bucket/path/to/unique_video.mp4"
    assert content["upload_name"] == "unique_video.mp4"


@pytest.mark.asyncio
async def test_read_video_upload_by_id_not_found(client, superuser_token_headers) -> None:
    response = await client.get(
        "/api/v1/video-uploads/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_video_upload(client, superuser_token_headers, db_session: AsyncSession) -> None:
    create_response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/original.mp4",
            "upload_name": "original.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]
    update_data = {
        "upload_location": "s3://videos/bucket/path/to/updated.mp4",
        "upload_name": "updated.mp4",
    }
    response = await client.patch(
        f"/api/v1/video-uploads/{video_upload_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
    assert content["upload_name"] == "updated.mp4"
    assert content["updated_on"] is not None


@pytest.mark.asyncio
async def test_update_video_upload_not_found(client, superuser_token_headers) -> None:
    response = await client.patch(
        "/api/v1/video-uploads/00000000-0000-0000-0000-000000000000",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/updated.mp4",
            "upload_name": "updated.mp4",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_video_upload(client, superuser_token_headers, db_session: AsyncSession) -> None:
    create_response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/delete_me.mp4",
            "upload_name": "delete_me.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]
    response = await client.delete(
        f"/api/v1/video-uploads/{video_upload_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Video upload deleted successfully"
    get_response = await client.get(f"/api/v1/video-uploads/{video_upload_id}", headers=superuser_token_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_video_upload_not_found(client, superuser_token_headers) -> None:
    response = await client.delete(
        "/api/v1/video-uploads/00000000-0000-0000-0000-000000000000", headers=superuser_token_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination(client, superuser_token_headers, db_session: AsyncSession) -> None:
    for i in range(10):
        await client.post(
            "/api/v1/video-uploads/",
            headers=superuser_token_headers,
            json={
                "upload_location": f"s3://videos/bucket/path/to/video{i}.mp4",
                "upload_name": f"video{i}.mp4",
            },
        )
    response = await client.get("/api/v1/video-uploads/", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 10
    response = await client.get("/api/v1/video-uploads/?skip=5&limit=3", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 3
    response = await client.get("/api/v1/video-uploads/?limit=2", headers=superuser_token_headers)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 10
    assert len(content["data"]) == 2


@pytest.mark.asyncio
async def test_video_upload_validation(client, superuser_token_headers) -> None:
    response = await client.post("/api/v1/video-uploads/", headers=superuser_token_headers, json={})
    assert response.status_code == 422

    response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={"upload_name": "test.mp4"},
    )
    assert response.status_code == 422

    response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={"upload_location": "s3://videos/bucket/test.mp4"},
    )
    assert response.status_code == 422

    long_location = "s3://videos/" + "a" * 1000 + ".mp4"
    response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": long_location,
            "upload_name": "test.mp4",
        },
    )
    assert response.status_code == 422

    long_name = "a" * 1001
    response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/test.mp4",
            "upload_name": long_name,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_video_upload_update_partial_fields(client, superuser_token_headers, db_session: AsyncSession) -> None:
    create_response = await client.post(
        "/api/v1/video-uploads/",
        headers=superuser_token_headers,
        json={
            "upload_location": "s3://videos/bucket/path/to/original.mp4",
            "upload_name": "original.mp4",
        },
    )
    video_upload_id = create_response.json()["id"]
    response = await client.patch(
        f"/api/v1/video-uploads/{video_upload_id}",
        headers=superuser_token_headers,
        json={"upload_location": "s3://videos/bucket/path/to/updated.mp4"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
    assert content["upload_name"] == "original.mp4"

    response = await client.patch(
        f"/api/v1/video-uploads/{video_upload_id}",
        headers=superuser_token_headers,
        json={"upload_name": "updated.mp4"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["upload_location"] == "s3://videos/bucket/path/to/updated.mp4"
    assert content["upload_name"] == "updated.mp4"

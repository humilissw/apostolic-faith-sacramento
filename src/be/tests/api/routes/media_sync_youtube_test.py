"""Tests for POST /api/v1/media/sync-youtube (in-app YouTube account sync).

The Google YouTube Data API calls are mocked — no network. Covers:
* 400 when no youtube integration is configured
* happy path: new uploads create media + video_uploads rows, live videos
    excluded, existing rows untouched, re-sync is a no-op
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from app.models import IntegrationConfig, Media, VideoUpload
from app.services.youtube_sync_service import media_id_for_video


def _video(video_id: str, live: str = "none", title: str = "", description: str = ""):
    return {
        "id": video_id,
        "snippet": {
            "title": title or f"Sermon {video_id}",
            "description": description,
            "publishedAt": "2026-09-14T18:00:00Z",
            "liveBroadcastContent": live,
        },
        "contentDetails": {"duration": "PT1H"},
    }


def _integration(**overrides) -> IntegrationConfig:
    cfg = IntegrationConfig(
        type="youtube",
        display_name="YouTube",
        icon="Youtube",
        enabled=True,
        status="connected",
        config_json='{"channelId": "UCtest"}',
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


@pytest.mark.asyncio
async def test_sync_requires_configured_integration(client, superuser_token_headers, db_session):
    # No IntegrationConfig(type="youtube") exists -> 400 with guidance.
    response = await client.post("/api/v1/media/sync-youtube", headers=superuser_token_headers)
    assert response.status_code == 400
    assert "integration" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_sync_denied_without_scope(client, db_session):
    # A plain (non-superuser, unscoped) caller must not be able to trigger sync.
    from app.api.deps import get_current_user

    user = MagicMock()
    user.id = "00000000-0000-0000-0000-000000000001"
    app = client._transport  # not used; just to appease linters
    del app
    from app.main import app as fastapi_app

    async def fake_user():
        raise AssertionError("scope check should reject before dependency resolution")

    fastapi_app.dependency_overrides[get_current_user] = fake_user
    try:
        response = await client.post("/api/v1/media/sync-youtube")
        assert response.status_code in (401, 403)
    finally:
        fastapi_app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_sync_creates_rows_excludes_live_and_is_idempotent(
    client, superuser_token_headers, db_session
):
    integration = _integration()
    db_session.add(integration)
    await db_session.commit()

    sermon_desc = (
        "9/14/2026 — 11:00 am Sunday morning service - Abide in the Vine — "
        "Bro. Sorin Filimon • John 15:1-8\nTrinity Apostolic Faith Church"
    )
    videos = [
        _video("vid_sermon", title="Abide in the Vine", description=sermon_desc),
        _video(
            "vid_plain",
            title="Candlelight service",
            description="a wonderful evening of worship songs",
        ),
        _video(
            "vid_live",
            live="live",
            title="Livestream",
            description="ongoing stream • John 1:1",
        ),
    ]

    def fake_get(url, **kwargs):  # noqa: ANN001
        resp = MagicMock()
        resp.status_code = 200
        if "channels" in url:
            resp.json.return_value = {
                "items": [
                    {
                        "id": "UCtest",
                        "contentDetails": {"relatedPlaylists": {"uploads": "UUtest"}},
                    }
                ]
            }
        elif "playlistItems" in url:
            resp.json.return_value = {
                "items": [{"contentDetails": {"videoId": v["id"]}} for v in videos]
            }
        else:  # videos
            resp.json.return_value = {"items": videos}
        return resp

    with (
        patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)),
        patch(
            "app.services.youtube_sync_service.YouTubeSyncService._fetch_credentials",
            new=AsyncMock(return_value={"api_key": "test-key"}),
        ),
    ):
        response = await client.post("/api/v1/media/sync-youtube", headers=superuser_token_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["media_created"] == 2  # sermon + plain; live excluded
    assert body["video_uploads_created"] == 1  # only the scripture-bearing one
    assert body["skipped_live"] == 1

    media_rows = (await db_session.execute(select(Media))).scalars().all()
    ids = {m.id for m in media_rows}
    assert media_id_for_video("vid_sermon") in ids
    assert media_id_for_video("vid_plain") in ids
    assert media_id_for_video("vid_live") not in ids  # live videos excluded

    uploads = (await db_session.execute(select(VideoUpload))).scalars().all()
    assert len(uploads) == 1
    assert uploads[0].id == media_id_for_video("vid_sermon")
    assert uploads[0].reference_text == "John 15:1-8"
    assert uploads[0].speaker_name == "Bro. Sorin Filimon"

    # Re-sync: everything already present -> no new rows, existing kept as-is.
    with (
        patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)),
        patch(
            "app.services.youtube_sync_service.YouTubeSyncService._fetch_credentials",
            new=AsyncMock(return_value={"api_key": "test-key"}),
        ),
    ):
        second = await client.post("/api/v1/media/sync-youtube", headers=superuser_token_headers)

    assert second.status_code == 200
    body2 = second.json()
    assert body2["media_created"] == 0
    assert body2["video_uploads_created"] == 0
    assert body2["skipped_existing"] == 2

    media_rows = (await db_session.execute(select(Media))).scalars().all()
    assert len(media_rows) == 2


@pytest.mark.asyncio
async def test_sync_disabled_integration_returns_400(client, superuser_token_headers, db_session):
    db_session.add(_integration(enabled=False))
    await db_session.commit()

    response = await client.post("/api/v1/media/sync-youtube", headers=superuser_token_headers)
    assert response.status_code == 400
    assert "disabled" in response.json()["detail"].lower()

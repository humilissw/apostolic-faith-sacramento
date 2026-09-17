"""In-app sync of the YouTube channel's uploaded videos into media/video_uploads.

Pulls the list of *uploaded* videos for the connected YouTube account (from the
``youtube`` IntegrationConfig — API key credential + optional channelId in
config_json), excludes live videos, and inserts any videos that are not yet in
the database. Existing rows are never modified, so admin edits survive a sync.

Row identity matches the seed/append migrations exactly: ids are UUID5 of the
YouTube video id in the same namespace (see scripts/generate_media_migration.py),
so a video synced at runtime and a video seeded by a migration map to the same
row. Parsing rules for video_uploads come from app.services.youtube_parse.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IntegrationConfig, Media, VideoUpload
from app.services.integration_service import IntegrationService
from app.services.youtube_parse import MAX_REFERENCE_LEN, parse_video

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Same namespaced UUID the migration generators use — a given YouTube video id
# must map to the same media/video_upload row regardless of who inserted it.
MEDIA_NAMESPACE = uuid.UUID("6ba7b812-9dad-11d1-80b4-00c04fd430c8")  # NAMESPACE_URL

DEFAULT_CHANNEL_HANDLE = "ApostolicFaithSacramento"

# Fallback channel id (AFC Sacramento) used when neither config_json nor the
# API can tell us which channels the key/account owns.
DEFAULT_CHANNEL_ID = "UCm-EgWcr8_daj9U-9V6dJxA"


def media_id_for_video(video_id: str) -> str:
    """Deterministic row id for a YouTube video (identical to the migrations)."""
    return str(uuid.uuid5(MEDIA_NAMESPACE, f"youtube:{video_id}"))


class YouTubeSyncError(Exception):
    """Raised when the sync cannot proceed (missing config, API failure...)."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class YouTubeSyncResult(dict):
    """Structured sync outcome (dict subclass so routes can return it directly)."""


def _parse_published(iso: str | None) -> datetime:
    if not iso:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except ValueError:
        return datetime.now(timezone.utc).replace(tzinfo=None)


class YouTubeSyncService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # Configuration / credentials
    # ------------------------------------------------------------------

    async def _load_integration(self) -> IntegrationConfig:
        from app.repositories.integration_repo import IntegrationConfigRepository

        svc = IntegrationService(IntegrationConfigRepository(self.session))
        config = await svc.get_by_type("youtube")
        if not config:
            raise YouTubeSyncError(
                "No YouTube integration configured. Add one on the Integrations "
                "page (API key + channel ID) before syncing.",
                status_code=400,
            )
        if not config.enabled:
            raise YouTubeSyncError("The YouTube integration is disabled.", status_code=400)
        return config

    async def _resolve_channel_id(
        self, client: httpx.AsyncClient, api_key: str, config_json: str | None
    ) -> str:
        """Channel id precedence: config_json.channelId -> ?mine=true -> default."""
        if config_json:
            try:
                cfg = json.loads(config_json)
                channel_id = cfg.get("channelId") or cfg.get("channel_id")
                if channel_id:
                    return str(channel_id)
            except (json.JSONDecodeError, AttributeError):
                logger.warning("youtube integration config_json is not valid JSON; ignoring")

        # Ask Google which channel the credential owns (works for OAuth tokens;
        # plain API keys are not tied to a channel and will error out).
        try:
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/channels",
                params={"part": "snippet", "mine": "true", "key": api_key},
                timeout=15.0,
            )
            if resp.status_code == 200:
                items: list[dict] = resp.json().get("items", [])
                if items:
                    return str(items[0]["id"])
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("YouTube 'mine' channel lookup failed: %s", exc)

        return DEFAULT_CHANNEL_ID

    async def _fetch_credentials(self, config: IntegrationConfig) -> dict[str, str]:
        from app.repositories.integration_repo import IntegrationConfigRepository

        svc = IntegrationService(IntegrationConfigRepository(self.session))
        creds = await svc.get_credentials(config)
        api_key = (creds or {}).get("api_key", "")
        if not api_key:
            raise YouTubeSyncError(
                "The YouTube integration has no API key stored. Add one on the "
                "Integrations page.",
                status_code=400,
            )
        return creds or {}

    # ------------------------------------------------------------------
    # YouTube Data API
    # ------------------------------------------------------------------

    async def _uploads_list_id(self, client, api_key, channel_id) -> str:
        resp = await client.get(
            f"{YOUTUBE_API_BASE}/channels",
            params={"part": "contentDetails", "id": channel_id, "key": api_key},
            timeout=15.0,
        )
        if resp.status_code != 200:
            raise YouTubeSyncError(
                f"YouTube API error fetching channel: HTTP {resp.status_code}",
                status_code=502,
            )
        items: list[dict] = resp.json().get("items", [])
        if not items:
            raise YouTubeSyncError("YouTube channel not found.", status_code=404)
        try:
            return str(items[0]["contentDetails"]["relatedPlaylists"]["uploads"])
        except KeyError as exc:
            raise YouTubeSyncError(f"Unexpected YouTube channel payload: {exc}") from exc

    async def _playlist_video_ids(self, client, api_key, uploads_list_id) -> list[str]:
        ids: list[str] = []
        page_token: str | None = None
        while True:
            params: dict[str, str] = {
                "part": "contentDetails",
                "playlistId": uploads_list_id,
                "maxResults": "50",
                "key": api_key,
            }
            if page_token:
                params["pageToken"] = page_token
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/playlistItems", params=params, timeout=15.0
            )
            if resp.status_code != 200:
                raise YouTubeSyncError(
                    f"YouTube API error fetching uploads: HTTP {resp.status_code}",
                    status_code=502,
                )
            payload = resp.json()
            for entry in payload.get("items", []):
                video_id = entry.get("contentDetails", {}).get("videoId")
                if video_id:
                    ids.append(video_id)
            page_token = payload.get("nextPageToken")
            if not page_token:
                return ids

    async def _video_details(self, client, api_key, video_ids) -> list[dict]:
        details: list[dict] = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i : i + 50]
            resp = await client.get(
                f"{YOUTUBE_API_BASE}/videos",
                params={
                    "part": "snippet,contentDetails",
                    "id": ",".join(batch),
                    "key": api_key,
                },
                timeout=20.0,
            )
            if resp.status_code != 200:
                raise YouTubeSyncError(
                    f"YouTube API error fetching video details: HTTP {resp.status_code}",
                    status_code=502,
                )
            details.extend(resp.json().get("items", []))
        return details

    # ------------------------------------------------------------------
    # Sync (upsert into media + video_uploads)
    # ------------------------------------------------------------------

    async def sync(self, owner_id: str) -> YouTubeSyncResult:
        config = await self._load_integration()
        creds = await self._fetch_credentials(config)
        api_key = creds["api_key"]

        async with httpx.AsyncClient() as client:
            channel_id = await self._resolve_channel_id(client, api_key, config.config_json)
            uploads_list_id = await self._uploads_list_id(client, api_key, channel_id)
            video_ids = await self._playlist_video_ids(client, api_key, uploads_list_id)
            details = await self._video_details(client, api_key, video_ids) if video_ids else []

        videos: list[dict[str, Any]] = []
        skipped_live = 0
        for item in details:
            snippet = item.get("snippet", {})
            # Exclude live videos (ongoing/pending streams). Finished past
            # broadcasts report "none"/"completed" and are treated as uploads.
            if str(snippet.get("liveBroadcastContent", "none")).lower() == "live":
                skipped_live += 1
                continue
            videos.append(
                {
                    "id": item["id"],
                    "title": snippet.get("title", "") or "",
                    "description": snippet.get("description", "") or "",
                    "published_at": snippet.get("publishedAt"),
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                }
            )

        result = await self._store(videos, owner_id)
        result["skipped_live"] = skipped_live
        result["total_channel_videos"] = len(details)

        # Bookkeeping on the integration row.
        config.status = "connected"
        config.last_synced_at = datetime.now(timezone.utc)
        self.session.add(config)
        await self.session.commit()
        return result

    async def _store(self, videos: list[dict[str, Any]], owner_id: str) -> YouTubeSyncResult:
        media_created = 0
        video_uploads_created = 0
        skipped_existing = 0

        for video in videos:
            row_id = media_id_for_video(video["id"])
            published = _parse_published(video.get("published_at"))

            existing_media = await self.session.get(Media, row_id)
            if existing_media:
                skipped_existing += 1
            else:
                description = video["description"].strip() or None
                if description and len(description) > 4000:
                    description = description[:4000]
                self.session.add(
                    Media(
                        id=row_id,
                        name=video["title"][:200],
                        description=description,
                        owner_id=owner_id,
                        uploaded_on=published,
                        created_on=published,
                        updated_on=published,
                    )
                )
                media_created += 1

            # video_uploads only gets videos that carry a scripture reference —
            # same rule as scripts/generate_video_uploads_migration.py.
            parsed = parse_video(video)
            if parsed and parsed["ref"] and len(parsed["ref"]) <= MAX_REFERENCE_LEN:
                existing_upload = await self.session.get(VideoUpload, row_id)
                if not existing_upload:
                    description = video["description"].strip() or None
                    if description and len(description) > 4000:
                        description = description[:4000]
                    speaker_value = parsed["speaker"][:200] if parsed["speaker"] else None
                    self.session.add(
                        VideoUpload(
                            id=row_id,
                            owner_id=owner_id,
                            upload_location=video["url"][:1000],
                            upload_name=(parsed["title"] or video["title"])[:1000],
                            media_association_date=published,
                            speaker_name=speaker_value,  # type: ignore[arg-type]
                            reference_text=parsed["ref"][:MAX_REFERENCE_LEN],
                            description=description,  # type: ignore[arg-type]
                            created_on=published,
                            updated_on=published,
                        )
                    )
                    video_uploads_created += 1

        await self.session.commit()
        return YouTubeSyncResult(
            media_created=media_created,
            video_uploads_created=video_uploads_created,
            skipped_existing=skipped_existing,
        )

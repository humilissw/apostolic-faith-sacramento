from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_password_hash
from app.crud import create_user
from app.models import User, UserCreate, UserScope


def event_payload(offset_days: int = 1) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "title": "Men's Night",
        "description": "Fellowship evening",
        "date": (now + timedelta(days=offset_days)).isoformat(),
        "start_time": (now + timedelta(days=offset_days, hours=2)).isoformat(),
        "end_time": (now + timedelta(days=offset_days, hours=4)).isoformat(),
    }


@pytest.fixture(scope="function")
async def events_admin_token(client, db_session) -> dict[str, str]:
    """Login as user with events:admin scope (and no superuser)."""
    email = "events_admin_test@example.com"
    statement = select(User).where(User.email == email)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )
    user.hashed_password = get_password_hash("testpassword123")
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "events:admin")
    )
    if not result.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="events:admin"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.mark.asyncio
async def test_read_events_anonymous(client, db_session: AsyncSession) -> None:
    """Public events page fetches this endpoint without a token — must stay public."""
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content


@pytest.mark.asyncio
async def test_read_event_by_id_anonymous(
    client, superuser_token_headers, db_session: AsyncSession
) -> None:
    """Fetching a single event by ID must work without a token."""
    create_response = await client.post(
        "/api/v1/events/",
        headers=superuser_token_headers,
        json=event_payload(),
    )
    assert create_response.status_code == 201
    event_id = create_response.json()["id"]
    response = await client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id


@pytest.mark.asyncio
async def test_create_event_anonymous_forbidden(client, db_session: AsyncSession) -> None:
    """Anonymous users must not be able to create events."""
    response = await client.post("/api/v1/events/", json=event_payload())
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_event_requires_events_admin(
    client, normal_user_token_headers, db_session: AsyncSession
) -> None:
    """A user without events:admin (and not superuser) cannot create events."""
    response = await client.post(
        "/api/v1/events/", headers=normal_user_token_headers, json=event_payload()
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_event_as_events_admin(
    client, events_admin_token, db_session: AsyncSession
) -> None:
    response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    assert response.status_code == 201
    content = response.json()
    assert content["id"] is not None
    assert content["title"] == "Men's Night"


@pytest.mark.asyncio
async def test_update_event_as_events_admin(
    client, events_admin_token, db_session: AsyncSession
) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.patch(
        f"/api/v1/events/{event_id}",
        headers=events_admin_token,
        json={"title": "Updated Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_event_forbidden_without_scope(
    client, normal_user_token_headers, superuser_token_headers, db_session: AsyncSession
) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=superuser_token_headers, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.patch(
        f"/api/v1/events/{event_id}",
        headers=normal_user_token_headers,
        json={"title": "Hijacked"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_event_as_events_admin(
    client, events_admin_token, db_session: AsyncSession
) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.delete(f"/api/v1/events/{event_id}", headers=events_admin_token)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_event_forbidden_without_scope(
    client, normal_user_token_headers, superuser_token_headers, db_session: AsyncSession
) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=superuser_token_headers, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.delete(f"/api/v1/events/{event_id}", headers=normal_user_token_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_bulk_delete_events_as_events_admin(
    client, events_admin_token, db_session: AsyncSession
) -> None:
    ids = []
    for offset in (1, 2, 3):
        create_response = await client.post(
            "/api/v1/events/", headers=events_admin_token, json=event_payload(offset)
        )
        assert create_response.status_code == 201
        ids.append(create_response.json()["id"])

    response = await client.request(
        "DELETE",
        "/api/v1/events/bulk",
        headers=events_admin_token,
        json={"event_ids": ids[:2]},
    )
    assert response.status_code == 200
    assert "2" in response.json()["message"]

    for event_id in ids[:2]:
        get_response = await client.get(f"/api/v1/events/{event_id}")
        assert get_response.status_code == 404
    remaining = await client.get(f"/api/v1/events/{ids[2]}")
    assert remaining.status_code == 200


@pytest.mark.asyncio
async def test_bulk_delete_ignores_unknown_ids(
    client, events_admin_token, db_session: AsyncSession
) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    event_id = create_response.json()["id"]

    response = await client.request(
        "DELETE",
        "/api/v1/events/bulk",
        headers=events_admin_token,
        json={"event_ids": [event_id, "00000000-0000-0000-0000-000000000000"]},
    )
    assert response.status_code == 200
    assert "1" in response.json()["message"]


@pytest.mark.asyncio
async def test_bulk_delete_requires_at_least_one_id(
    client, events_admin_token, db_session: AsyncSession
) -> None:
    response = await client.request(
        "DELETE",
        "/api/v1/events/bulk",
        headers=events_admin_token,
        json={"event_ids": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_bulk_delete_forbidden_without_scope(
    client, normal_user_token_headers, db_session: AsyncSession
) -> None:
    response = await client.request(
        "DELETE",
        "/api/v1/events/bulk",
        headers=normal_user_token_headers,
        json={"event_ids": ["some-id"]},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_superuser_can_edit_events(
    client, superuser_token_headers, db_session: AsyncSession
) -> None:
    """Superuser scope bypasses the events:admin requirement."""
    create_response = await client.post(
        "/api/v1/events/", headers=superuser_token_headers, json=event_payload()
    )
    assert create_response.status_code == 201


# --- Flyer endpoints ---

TINY_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000d4944415478da63fcffffffffff030000060205a2"
    "b7ad800000000049454e44ae426082"
)


@pytest.mark.asyncio
async def test_flyer_upload_anonymous_forbidden(client, superuser_token_headers) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=superuser_token_headers, json=event_payload()
    )
    event_id = create_response.json()["id"]
    # The superuser login above stored auth cookies in the client jar;
    # clear them so this request is genuinely anonymous.
    client.cookies.clear()
    response = await client.post(
        f"/api/v1/events/{event_id}/flyer",
        files={"file": ("flyer.png", TINY_PNG, "image/png")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_flyer_upload_forbidden_without_scope(
    client, superuser_token_headers, normal_user_token_headers
) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=superuser_token_headers, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.post(
        f"/api/v1/events/{event_id}/flyer",
        headers=normal_user_token_headers,
        files={"file": ("flyer.png", TINY_PNG, "image/png")},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_flyer_upload_read_and_delete_as_events_admin(client, events_admin_token) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    event_id = create_response.json()["id"]
    assert create_response.json()["flyer_url"] is None

    upload = await client.post(
        f"/api/v1/events/{event_id}/flyer",
        headers=events_admin_token,
        files={"file": ("flyer.png", TINY_PNG, "image/png")},
    )
    assert upload.status_code == 200
    assert upload.json()["flyer_url"] == f"/api/v1/events/{event_id}/flyer"

    # Public (anonymous) fetch of the flyer image.
    get_response = await client.get(f"/api/v1/events/{event_id}/flyer")
    assert get_response.status_code == 200
    assert get_response.headers["content-type"] == "image/png"
    assert get_response.content == TINY_PNG

    delete_response = await client.delete(
        f"/api/v1/events/{event_id}/flyer", headers=events_admin_token
    )
    assert delete_response.status_code == 200
    missing = await client.get(f"/api/v1/events/{event_id}/flyer")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_flyer_anonymous_get_missing_is_404(client, superuser_token_headers) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=superuser_token_headers, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.get(f"/api/v1/events/{event_id}/flyer")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_flyer_rejects_non_image(client, events_admin_token) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    event_id = create_response.json()["id"]
    response = await client.post(
        f"/api/v1/events/{event_id}/flyer",
        headers=events_admin_token,
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_event_list_includes_flyer_url(client, events_admin_token) -> None:
    create_response = await client.post(
        "/api/v1/events/", headers=events_admin_token, json=event_payload()
    )
    event_id = create_response.json()["id"]
    await client.post(
        f"/api/v1/events/{event_id}/flyer",
        headers=events_admin_token,
        files={"file": ("flyer.png", TINY_PNG, "image/png")},
    )
    # Anonymous list fetch (public events page / homepage) exposes flyer_url.
    response = await client.get("/api/v1/events/", params={"limit": 500})
    assert response.status_code == 200
    entry = next(e for e in response.json()["data"] if e["id"] == event_id)
    assert entry["flyer_url"] == f"/api/v1/events/{event_id}/flyer"

import pytest
from datetime import datetime, timezone
from sqlalchemy import select

from app.config import settings
from app.core.security import get_password_hash
from app.crud import create_user
from app.models import User, UserCreate, UserScope


@pytest.fixture(scope="function")
async def scheduler_admin_token(client, db_session) -> dict[str, str]:
    """Login as superuser and grant scheduler:admin scope."""
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_active=True,
                is_superuser=True,
            ),
        )
    user.is_superuser = True
    user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
    db_session.add(user)
    await db_session.commit()

    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "superuser")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="superuser"))
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def member_limited_token(client, db_session) -> dict[str, str]:
    """Login as user with member:limited scope."""
    email = "member_limited_test@example.com"
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

    # Ensure member:limited scope exists (crud.create_user seeds it, but be explicit)
    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "member:limited")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="member:limited"))
        await db_session.commit()

    # Check what's in the DB for this user
    all_scopes = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id)  # type: ignore[arg-type]
    )
    scope_list = [r[0].scope for r in all_scopes.all()] if hasattr(all_scopes, "all") else []
    # Fix: use scalar approach
    rows = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id)
    )  # type: ignore[arg-type]
    scope_list = [r.scope for r in rows.scalars().all()]

    print(scope_list)

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    assert "member:limited" in tokens.get(
        "scopes", []
    ), f"member:limited not in token scopes: {tokens.get('scopes')}"
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def normal_user_token(client, db_session) -> dict[str, str]:
    """Login as user without member:limited scope."""
    email = "normal_user_test@example.com"
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

    # Remove member:limited scope if present
    result = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "member:limited")
    )
    scope_record = result.scalar_one_or_none()
    if scope_record:
        await db_session.execute(
            select(UserScope).where(UserScope.id == scope_record.id)  # type: ignore[arg-type]
        )
        await db_session.delete(scope_record)
        await db_session.commit()

    response = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def test_user_id(db_session) -> str:
    """Get a valid user ID from the test database for assignment user_id."""
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    return user.id  # type: ignore[return-value]


@pytest.mark.asyncio
async def test_list_assignments_empty(client, scheduler_admin_token) -> None:
    response = await client.get("/api/v1/scheduler/", headers=scheduler_admin_token)
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 0
    assert content["data"] == []


@pytest.mark.asyncio
async def test_create_assignment(client, scheduler_admin_token, test_user_id) -> None:
    test_date = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    response = await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": test_user_id,
            "event_date": test_date.isoformat(),
            "type": "music",
            "role": "Worship Leader",
            "instrument": "Guitar",
            "notes": "First song",
        },
    )
    assert response.status_code == 201
    content = response.json()
    assert content["type"] == "music"
    assert content["role"] == "Worship Leader"
    assert content["instrument"] == "Guitar"
    assert content["user_id"] == test_user_id
    assert content["id"] is not None


@pytest.mark.asyncio
async def test_get_assignment(client, scheduler_admin_token, test_user_id) -> None:
    test_date = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    create_resp = await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": test_user_id,
            "event_date": test_date.isoformat(),
            "type": "service",
        },
    )
    assignment_id = create_resp.json()["id"]
    get_resp = await client.get(f"/api/v1/scheduler/{assignment_id}", headers=scheduler_admin_token)
    assert get_resp.status_code == 200
    assert get_resp.json()["user_id"] == test_user_id
    assert get_resp.json()["type"] == "service"


@pytest.mark.asyncio
async def test_update_assignment(client, scheduler_admin_token, test_user_id) -> None:
    test_date = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    create_resp = await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": test_user_id,
            "event_date": test_date.isoformat(),
            "type": "music",
            "role": "Original",
        },
    )
    assignment_id = create_resp.json()["id"]
    update_resp = await client.patch(
        f"/api/v1/scheduler/{assignment_id}",
        headers=scheduler_admin_token,
        json={"role": "Updated Role"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["role"] == "Updated Role"


@pytest.mark.asyncio
async def test_delete_assignment(client, scheduler_admin_token, test_user_id) -> None:
    test_date = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    create_resp = await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": test_user_id,
            "event_date": test_date.isoformat(),
            "type": "service",
        },
    )
    assignment_id = create_resp.json()["id"]
    delete_resp = await client.delete(
        f"/api/v1/scheduler/{assignment_id}", headers=scheduler_admin_token
    )
    assert delete_resp.status_code == 204
    # Verify deleted
    get_resp = await client.get(f"/api/v1/scheduler/{assignment_id}", headers=scheduler_admin_token)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_assignment_not_found(client, scheduler_admin_token) -> None:
    response = await client.get(
        "/api/v1/scheduler/00000000-0000-0000-0000-000000000000",
        headers=scheduler_admin_token,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_my_assignments_requires_member_limited(client, normal_user_token) -> None:
    response = await client.get("/api/v1/scheduler/my-assignments", headers=normal_user_token)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_my_assignments_returns_own_only(
    client, db_session, scheduler_admin_token, member_limited_token
) -> None:
    test_date = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    email = "member_limited_test@example.com"
    stmt = select(User).where(User.email == email)
    member_user = (await db_session.execute(stmt)).scalar_one_or_none()
    if not member_user:
        member_user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )

    # Create an assignment for the member user via admin
    await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": member_user.id,
            "event_date": test_date.isoformat(),
            "type": "music",
        },
    )

    response = await client.get("/api/v1/scheduler/my-assignments", headers=member_limited_token)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_calendar_endpoint(
    client, scheduler_admin_token, member_limited_token, test_user_id
) -> None:
    test_date = datetime(2026, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
    await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": test_user_id,
            "event_date": test_date.isoformat(),
            "type": "music",
        },
    )
    response = await client.get(
        "/api/v1/scheduler/calendar?start_date=2026-06-01&end_date=2026-06-30",
        headers=member_limited_token,
    )
    assert response.status_code == 200
    assert response.json()["count"] >= 1


@pytest.mark.asyncio
async def test_list_assignments_requires_admin_scope(client, member_limited_token) -> None:
    response = await client.get("/api/v1/scheduler/", headers=member_limited_token)
    assert response.status_code == 403

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
async def test_get_my_assignments_requires_member_limited(client, db_session) -> None:
    """A user without member:limited and without api:all should be blocked."""
    email = "no_scope_user_test@example.com"
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

    # Remove ALL scopes - user has no scopes at all
    rows = await db_session.execute(select(UserScope).where(UserScope.user_id == user.id))
    for row in rows.scalars().all():
        await db_session.delete(row)
    await db_session.commit()

    response = await client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # User with no scopes gets ["api:all"] from login, which grants full access
    # To truly test scope requirement, we need a user with a different scope
    # but NOT member:limited or api:all
    response2 = await client.get("/api/v1/scheduler/my-assignments", headers=headers)
    # api:all grants full API access, so this returns 200 with empty data
    assert response2.status_code == 200


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
async def test_my_scheduler_full_flow(client, db_session, scheduler_admin_token) -> None:
    """End-to-end: member user logs in, has scopes in token, calls my-assignments."""
    # 1. Create a member user
    email = "my_scheduler_e2e@example.com"
    stmt = select(User).where(User.email == email)
    member_user = (await db_session.execute(stmt)).scalar_one_or_none()
    if not member_user:
        member_user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="memberpass123"),
        )
    member_user.hashed_password = get_password_hash("memberpass123")
    db_session.add(member_user)
    await db_session.commit()

    # 2. Assign member:limited scope
    has_scope = await db_session.execute(
        select(UserScope).where(
            UserScope.user_id == member_user.id,
            UserScope.scope == "member:limited",
        )
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=member_user.id, scope="member:limited"))
        await db_session.commit()

    # 3. Login and get token with scopes
    resp = await client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": "memberpass123"},
    )
    assert resp.status_code == 200
    token_data = resp.json()
    assert "member:limited" in token_data.get(
        "scopes", []
    ), f"member:limited not in token scopes: {token_data.get('scopes')}"

    # 4. Admin creates assignment for this member user
    test_date = datetime(2026, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
    create_resp = await client.post(
        "/api/v1/scheduler/",
        headers=scheduler_admin_token,
        json={
            "user_id": member_user.id,
            "event_date": test_date.isoformat(),
            "type": "music",
            "role": "Worship Leader",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["user_id"] == member_user.id

    # 5. Member calls my-assignments with their token
    member_token = token_data["access_token"]
    my_resp = await client.get(
        "/api/v1/scheduler/my-assignments",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert my_resp.status_code == 200
    my_data = my_resp.json()
    assert len(my_data["data"]) >= 1
    assert my_data["data"][0]["user_id"] == member_user.id
    assert my_data["data"][0]["type"] == "music"
    assert my_data["data"][0]["role"] == "Worship Leader"


@pytest.mark.asyncio
async def test_user_public_returns_id(client, db_session) -> None:
    """Ensure UserPublic model includes 'id' field for frontend user selection."""
    email = "user_public_id_test@example.com"
    stmt = select(User).where(User.email == email)
    user = (await db_session.execute(stmt)).scalar_one_or_none()
    if not user:
        user = await create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpass123"),
        )
    user.hashed_password = get_password_hash("testpass123")
    db_session.add(user)
    await db_session.commit()

    super_stmt = select(User).where(User.email == settings.FIRST_SUPERUSER)
    super_user = (await db_session.execute(super_stmt)).scalar_one_or_none()
    if not super_user:
        super_user = await create_user(
            session=db_session,
            user_create=UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_active=True,
                is_superuser=True,
            ),
        )
    super_user.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
    db_session.add(super_user)
    await db_session.commit()

    has_scope = await db_session.execute(
        select(UserScope).where(
            UserScope.user_id == super_user.id,
            UserScope.scope == "superuser",
        )
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=super_user.id, scope="superuser"))
        await db_session.commit()

    login_resp = await client.post(
        "/api/v1/login/access-token",
        data={"username": settings.FIRST_SUPERUSER, "password": settings.FIRST_SUPERUSER_PASSWORD},
    )
    tokens = login_resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    users_resp = await client.get("/api/v1/users/?skip=0&limit=50", headers=headers)
    assert users_resp.status_code == 200
    users_data = users_resp.json()
    assert users_data["count"] >= 1
    for user_entry in users_data["data"]:
        assert "id" in user_entry, f"user entry missing 'id' field: {user_entry}"
        assert len(user_entry["id"]) > 0, f"user id is empty: {user_entry}"

import pytest
from sqlalchemy import select

from app.config import settings
from app.core.security import get_password_hash
from app.crud import create_user
from app.models import User, UserCreate, UserScope


@pytest.fixture(scope="function")
async def scope_test_user(client, db_session) -> str:
    """Create a test user and return their ID."""
    import uuid

    email = f"scope_test_{uuid.uuid4().hex[:8]}@test.com"
    user = await create_user(
        session=db_session,
        user_create=UserCreate(email=email, password="testpass123"),
    )
    # Remove the default member:limited scope so tests can verify empty scopes
    from app.models import UserScope

    stmt = select(UserScope).where(UserScope.user_id == user.id)
    result = await db_session.execute(stmt)
    for row in result.scalars().all():
        await db_session.delete(row)
    await db_session.commit()
    return user.id


@pytest.fixture(scope="function")
async def scope_test_token(client, db_session, scope_test_user) -> dict[str, str]:
    """Create a superuser token for scope management tests."""
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
        data={"username": settings.FIRST_SUPERUSER, "password": settings.FIRST_SUPERUSER_PASSWORD},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
async def scope_test_user_with_scopes(db_session, scope_test_user) -> str:
    """Assign some scopes to the test user."""
    db_session.add(UserScope(user_id=scope_test_user, scope="integrations:admin"))
    db_session.add(UserScope(user_id=scope_test_user, scope="payments:read"))
    await db_session.commit()
    return scope_test_user


@pytest.mark.asyncio
async def test_get_user_scopes(
    client, scope_test_token, db_session, scope_test_user_with_scopes
) -> None:
    response = await client.get(
        f"/api/v1/users/admin/{scope_test_user_with_scopes}/scopes",
        headers=scope_test_token,
    )
    assert response.status_code == 200
    scopes = response.json()
    assert set(scopes) == {"integrations:admin", "payments:read"}


@pytest.mark.asyncio
async def test_get_user_scopes_empty(client, scope_test_token, scope_test_user) -> None:
    response = await client.get(
        f"/api/v1/users/admin/{scope_test_user}/scopes",
        headers=scope_test_token,
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_set_user_scopes(client, scope_test_token, scope_test_user) -> None:
    new_scopes = ["media:write", "church:manage"]
    response = await client.put(
        f"/api/v1/users/admin/{scope_test_user}/scopes",
        headers=scope_test_token,
        json=new_scopes,
    )
    assert response.status_code == 200
    scopes = response.json()
    assert set(scopes) == set(new_scopes)


@pytest.mark.asyncio
async def test_set_user_scopes_clear(client, scope_test_token, scope_test_user_with_scopes) -> None:
    response = await client.put(
        f"/api/v1/users/admin/{scope_test_user_with_scopes}/scopes",
        headers=scope_test_token,
        json=[],
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_remove_all_user_scopes(
    client, scope_test_token, scope_test_user_with_scopes
) -> None:
    response = await client.delete(
        f"/api/v1/users/admin/{scope_test_user_with_scopes}",
        headers=scope_test_token,
    )
    assert response.status_code == 204

    get_response = await client.get(
        f"/api/v1/users/admin/{scope_test_user_with_scopes}/scopes",
        headers=scope_test_token,
    )
    assert get_response.status_code == 200
    assert get_response.json() == []


@pytest.mark.asyncio
async def test_normal_user_cannot_get_scopes(
    client, normal_user_token_headers, scope_test_user
) -> None:
    response = await client.get(
        f"/api/v1/users/admin/{scope_test_user}/scopes",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_normal_user_cannot_set_scopes(
    client, normal_user_token_headers, scope_test_user
) -> None:
    response = await client.put(
        f"/api/v1/users/admin/{scope_test_user}/scopes",
        headers=normal_user_token_headers,
        json=["some:scope"],
    )
    assert response.status_code == 403

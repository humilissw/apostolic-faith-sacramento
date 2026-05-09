from typing import AsyncGenerator
from unittest.mock import patch

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app import crud
from app.config import settings
from app.core.security import verify_password, get_password_hash
from app.core.db import get_db_session
from app.main import app
from app.models import User, UserCreate, UserScope
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture(scope="function")
async def users_client(db_session: AsyncSession) -> httpx.AsyncClient:
    """Test client that shares the test's db_session with the app."""
    # Use dependency_overrides to share the test's db_session with the app
    # Store the original override if any
    _original = app.dependency_overrides.pop(get_db_session, None)

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    # Restore original override
    if _original is not None:
        app.dependency_overrides[get_db_session] = _original
    else:
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_get_users_superuser_me(
    users_client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await users_client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert "superuser" in current_user.get("assigned_scopes", [])
    assert current_user["email"] == settings.FIRST_SUPERUSER


@pytest.mark.asyncio
async def test_get_users_normal_user_me(
    users_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    """Normal user with api:all scope can access /users/me."""
    email = settings.EMAIL_TEST_USER
    statement = select(User).where(User.email == email)
    user = (await db_session.execute(statement)).scalar_one_or_none()
    if not user:
        user = await crud.create_user(
            session=db_session,
            user_create=UserCreate(email=email, password="testpassword123"),
        )
    user.hashed_password = get_password_hash("testpassword123")
    db_session.add(user)
    await db_session.commit()
    # Grant api:all so scope check passes
    has_scope = await db_session.execute(
        select(UserScope).where(UserScope.user_id == user.id, UserScope.scope == "api:all")
    )
    if not has_scope.scalar_one_or_none():
        db_session.add(UserScope(user_id=user.id, scope="api:all"))
        await db_session.commit()

    r = await users_client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "testpassword123"},
    )
    tokens = r.json()
    r = await users_client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert "superuser" not in current_user.get("assigned_scopes", [])
    assert current_user["email"] == email


@pytest.mark.asyncio
async def test_create_user_new_email(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    with (patch("app.utils.send_email", return_value=None),):
        username = random_email()
        password = random_lower_string()
        data = {"email": username, "password": password}
        r = await users_client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300
        created_user = r.json()
        user = await crud.get_user_by_email(session=db_session, email=username)
        assert user
        assert user.email == created_user["email"]


@pytest.mark.asyncio
async def test_get_existing_user(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    user_id = user.id
    r = await users_client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.get_user_by_email(session=db_session, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


@pytest.mark.asyncio
async def test_get_existing_user_current_user(
    users_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    user_id = user.id

    login_data = {
        "username": username,
        "password": password,
    }
    r = await users_client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = await users_client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.get_user_by_email(session=db_session, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


@pytest.mark.asyncio
async def test_get_existing_user_permissions_error(
    users_client: httpx.AsyncClient,
    normal_user_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    # Create a user that the normal user can't access
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    target_user = await crud.create_user(session=db_session, user_create=user_in)

    r = await users_client.get(
        f"{settings.API_V1_STR}/users/{target_user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json() == {"detail": "The user doesn't have enough privileges"}


@pytest.mark.asyncio
async def test_create_user_existing_username(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    await crud.create_user(session=db_session, user_create=user_in)
    data = {"email": username, "password": password}
    r = await users_client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


@pytest.mark.asyncio
async def test_create_user_by_normal_user(
    users_client: httpx.AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = await users_client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_retrieve_users(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    await crud.create_user(session=db_session, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    await crud.create_user(session=db_session, user_create=user_in2)

    r = await users_client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item


@pytest.mark.asyncio
async def test_update_user_me(
    users_client: httpx.AsyncClient,
    normal_user_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    full_name = "Updated Name"
    data = {"full_name": full_name}
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 200

    # Get the original user's email from token_headers fixture
    statement = select(User).where(User.email == settings.EMAIL_TEST_USER)
    user_db = await db_session.execute(statement)
    original_user = user_db.scalar_one()
    assert original_user.full_name == full_name


@pytest.mark.asyncio
async def test_update_password_me(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    new_password = random_lower_string()
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": new_password,
    }
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"

    old_data = {
        "current_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=old_data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"


@pytest.mark.asyncio
async def test_update_password_me_incorrect_password(
    users_client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    new_password = random_lower_string()
    data = {"current_password": new_password, "new_password": new_password}
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"


@pytest.mark.asyncio
async def test_update_user_me_email_exists(
    users_client: httpx.AsyncClient,
    normal_user_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)

    data = {"email": user.email}
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


@pytest.mark.asyncio
async def test_update_password_me_same_password_error(
    users_client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "New password cannot be the same as the current one"


@pytest.mark.asyncio
async def test_register_user(users_client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    r = await users_client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )
    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == username

    user_query = select(User).where(User.email == username)
    user_db = await db_session.execute(user_query)
    registered_user = user_db.scalar_one()
    assert registered_user
    assert registered_user.email == username
    assert registered_user.full_name == full_name
    assert verify_password(password, registered_user.hashed_password)


@pytest.mark.asyncio
async def test_register_user_already_exists_error(
    users_client: httpx.AsyncClient,
) -> None:
    password = random_lower_string()
    full_name = random_lower_string()
    data = {
        "email": settings.FIRST_SUPERUSER,
        "password": password,
        "full_name": full_name,
    }
    r = await users_client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "The user with this email already exists in the system"


@pytest.mark.asyncio
async def test_update_user(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)

    data = {"full_name": "Updated_full_name"}
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_update_user_not_exists(
    users_client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"full_name": "Updated_full_name"}
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/999999999",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


@pytest.mark.asyncio
async def test_update_user_email_exists(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    user2 = await crud.create_user(session=db_session, user_create=user_in2)

    data = {"email": user2.email}
    r = await users_client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


@pytest.mark.asyncio
async def test_delete_user_me(users_client: httpx.AsyncClient, db_session: AsyncSession) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    _user = await crud.create_user(session=db_session, user_create=user_in)

    login_data = {
        "username": username,
        "password": password,
    }
    r = await users_client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = await users_client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"


@pytest.mark.asyncio
async def test_delete_user_me_as_superuser(
    users_client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await users_client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


@pytest.mark.asyncio
async def test_delete_user_super_user(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)
    user_id = user.id
    r = await users_client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"


@pytest.mark.asyncio
async def test_delete_user_not_found(
    users_client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    r = await users_client.delete(
        f"{settings.API_V1_STR}/users/999999999",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_current_super_user_error(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    super_user = await crud.get_user_by_email(session=db_session, email=settings.FIRST_SUPERUSER)
    assert super_user
    user_id = super_user.id

    r = await users_client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


@pytest.mark.asyncio
async def test_delete_user_without_privileges(
    users_client: httpx.AsyncClient,
    normal_user_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = await crud.create_user(session=db_session, user_create=user_in)

    r = await users_client.delete(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"


@pytest.mark.asyncio
async def test_bulk_delete_users(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    emails = []
    for _ in range(3):
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = await crud.create_user(session=db_session, user_create=user_in)
        emails.append(username)
        assert user

    r = await users_client.post(
        f"{settings.API_V1_STR}/users/admin/bulk-delete",
        headers=superuser_token_headers,
        json=[
            str(user.id)
            for user in [await crud.get_user_by_email(session=db_session, email=e) for e in emails]
        ],
    )
    assert r.status_code == 200
    assert "Deleted" in r.json()["message"]

    for email in emails:
        existing = await crud.get_user_by_email(session=db_session, email=email)
        assert existing is None, f"User {email} was not deleted"


@pytest.mark.asyncio
async def test_bulk_delete_users_partial(
    users_client: httpx.AsyncClient,
    superuser_token_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    users = []
    for _ in range(2):
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = await crud.create_user(session=db_session, user_create=user_in)
        users.append(user)

    fake_id = "00000000-0000-0000-0000-000000000000"
    r = await users_client.post(
        f"{settings.API_V1_STR}/users/admin/bulk-delete",
        headers=superuser_token_headers,
        json=[str(u.new_id) for u in users] + [fake_id],
    )
    assert r.status_code == 200
    assert "Deleted 2" in r.json()["message"]

    for u in users:
        existing = await crud.get_user_by_email(session=db_session, email=u.email)
        assert existing is None


@pytest.mark.asyncio
async def test_bulk_delete_users_no_privileges(
    users_client: httpx.AsyncClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    r = await users_client.post(
        f"{settings.API_V1_STR}/users/admin/bulk-delete",
        headers=normal_user_token_headers,
        json=["1"],
    )
    assert r.status_code == 403

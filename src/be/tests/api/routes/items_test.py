import uuid

import pytest

from tests.utils.item import create_random_item


@pytest.mark.asyncio
async def test_create_item(
    client, superuser_token_headers
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = await client.post(
        "/api/v1/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


@pytest.mark.asyncio
async def test_read_item(
    client, superuser_token_headers, db_session
) -> None:
    item = await create_random_item(db_session)
    response = await client.get(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id


@pytest.mark.asyncio
async def test_read_item_not_found(
    client, superuser_token_headers
) -> None:
    response = await client.get(
        "/api/v1/items/999999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_read_item_not_enough_permissions(
    client, normal_user_token_headers, db_session
) -> None:
    item = await create_random_item(db_session)
    response = await client.get(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


@pytest.mark.asyncio
async def test_read_items(
    client, superuser_token_headers, db_session
) -> None:
    await create_random_item(db_session)
    await create_random_item(db_session)
    response = await client.get(
        "/api/v1/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


@pytest.mark.asyncio
async def test_update_item(
    client, superuser_token_headers, db_session
) -> None:
    item = await create_random_item(db_session)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id


@pytest.mark.asyncio
async def test_update_item_not_found(
    client, superuser_token_headers
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        "/api/v1/items/999999999",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_update_item_not_enough_permissions(
    client, normal_user_token_headers, db_session
) -> None:
    item = await create_random_item(db_session)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


@pytest.mark.asyncio
async def test_delete_item(
    client, superuser_token_headers, db_session
) -> None:
    item = await create_random_item(db_session)
    response = await client.delete(
        f"/api/v1/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


@pytest.mark.asyncio
async def test_delete_item_not_found(
    client, superuser_token_headers
) -> None:
    response = await client.delete(
        "/api/v1/items/999999999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_delete_item_not_enough_permissions(
    client, normal_user_token_headers, db_session
) -> None:
    item = await create_random_item(db_session)
    response = await client.delete(
        f"/api/v1/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"

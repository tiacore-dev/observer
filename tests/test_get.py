import pytest
from httpx import AsyncClient

from app.database.models import Account, Chat


@pytest.fixture
async def seed_chat_account_role_data():
    await Chat.create(id=1, name="Чат 1")
    await Chat.create(id=2, name="Чат 2")
    await Account.create(id=1, username="user1", name="Аккаунт A")
    await Account.create(id=2, username="user2", name="Аккаунт B")

    yield


@pytest.mark.asyncio
async def test_get_chats(
    seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin: dict
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/chats/all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {c["chat_name"] for c in data["chats"]} == {"Чат 1", "Чат 2"}


@pytest.mark.asyncio
async def test_get_accounts(
    seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/accounts/all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {a["username"] for a in data["accounts"]} == {"user1", "user2"}


@pytest.mark.asyncio
async def test_chat_filtering_sorting(
    seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    # Фильтрация
    response = await test_app.get("/api/chats/all?chat_name=Чат 1", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1

    # Сортировка по убыванию
    response = await test_app.get(
        "/api/chats/all?sort_by=chat_name&order=desc", headers=headers
    )
    assert response.status_code == 200
    names = [c["chat_name"] for c in response.json()["chats"]]
    assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_account_pagination(
    seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(
        "/api/accounts/all?page=1&page_size=1", headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()["accounts"]) == 1
    assert response.json()["total"] == 2

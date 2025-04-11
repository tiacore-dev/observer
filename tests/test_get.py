import uuid
import pytest
from httpx import AsyncClient
from app.database.models import UserRoles, Chats, Accounts, Permissions


@pytest.fixture
async def seed_chat_account_role_data():
    await Chats.create(chat_id=1, chat_name="Чат 1")
    await Chats.create(chat_id=2, chat_name="Чат 2")
    await Accounts.create(account_id=1, username="user1", account_name="Аккаунт A")
    await Accounts.create(account_id=2, username="user2", account_name="Аккаунт B")
    role_1 = await UserRoles.create(role_id=uuid.uuid4(), role_name="Админ")
    role_2 = await UserRoles.create(role_id=uuid.uuid4(), role_name="Пользователь")

    await Permissions.create(permission_id=uuid.uuid4(), role=role_1)
    await Permissions.create(permission_id=uuid.uuid4(), role=role_2)
    yield


@pytest.mark.asyncio
async def test_get_chats(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/chats/all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {c["chat_name"] for c in data["chats"]} == {"Чат 1", "Чат 2"}


@pytest.mark.asyncio
async def test_get_accounts(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/accounts/all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {a["username"] for a in data["accounts"]} == {"user1", "user2"}


@pytest.mark.asyncio
async def test_get_user_roles_new(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/user-roles/all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert {r["role_name"]
            for r in data["roles"]} == {"Пользователь", "Админ"}


@pytest.mark.asyncio
async def test_chat_filtering_sorting(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    # Фильтрация
    response = await test_app.get("/api/chats/all?chat_name=Чат 1", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1

    # Сортировка по убыванию
    response = await test_app.get(
        "/api/chats/all?sort_by=chat_name&order=desc", headers=headers)
    assert response.status_code == 200
    names = [c["chat_name"] for c in response.json()["chats"]]
    assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_account_pagination(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(
        "/api/accounts/all?page=1&page_size=1", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["accounts"]) == 1
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_permissions(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/permissions/all", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    assert {p["role_name"]
            for p in data["permissions"]} == {"Админ", "Пользователь"}


@pytest.mark.asyncio
async def test_filter_permissions_by_role_name(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        "/api/permissions/all?role_name=Админ", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["permissions"][0]["role_name"] == "Админ"


@pytest.mark.asyncio
async def test_permission_pagination(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        "/api/permissions/all?page=1&page_size=1", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    assert len(data["permissions"]) == 1

    response2 = test_app.get(
        "/api/permissions/all?page=2&page_size=1", headers=headers)
    assert response2.status_code == 200
    assert len(response2.json()["permissions"]) == 1


@pytest.mark.asyncio
async def test_permission_sorting(seed_chat_account_role_data, test_app: AsyncClient, jwt_token_admin):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response_asc = test_app.get(
        "/api/permissions/all?sort_by=role__role_name&order=asc", headers=headers)
    response_desc = test_app.get(
        "/api/permissions/all?sort_by=role__role_name&order=desc", headers=headers)

    names_asc = [p["role_name"] for p in response_asc.json()["permissions"]]
    names_desc = [p["role_name"] for p in response_desc.json()["permissions"]]

    assert names_asc == sorted(names_asc)
    assert names_desc == sorted(names_asc, reverse=True)

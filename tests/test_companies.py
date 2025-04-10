import pytest
from httpx import AsyncClient
from app.database.models import Companies


@pytest.mark.asyncio
async def test_add_company(test_app: AsyncClient, jwt_token_admin):
    """Тест добавления новой компании."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_name": "Test Company",
        "description": "Описание тестовой компании"
    }

    response = test_app.post("/api/companies/add", headers=headers, json=data)
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    company = await Companies.filter(company_name="Test Company").first()
    assert data["company_id"] == str(company.company_id)


@pytest.mark.asyncio
async def test_edit_company(test_app: AsyncClient, jwt_token_admin, seed_company):
    """Тест редактирования компании."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "company_name": "Updated Company Name",
        "description": "Обновленное описание"
    }

    response = test_app.patch(
        f"/api/companies/{seed_company['company_id']}",
        headers=headers,
        json=data
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    # Проверяем, что данные обновились в БД
    updated_company = await Companies.filter(company_id=seed_company["company_id"]).first()
    assert updated_company is not None
    assert updated_company.company_name == "Updated Company Name"
    assert updated_company.description == "Обновленное описание"


@pytest.mark.asyncio
async def test_view_company(test_app: AsyncClient, jwt_token_admin, seed_company):
    """Тест просмотра информации о компании."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = test_app.get(
        f"/api/companies/{seed_company['company_id']}",
        headers=headers
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    assert response_data["company_id"] == str(seed_company["company_id"])
    assert response_data["company_name"] == seed_company["company_name"]


@pytest.mark.asyncio
async def test_delete_company(test_app: AsyncClient, jwt_token_admin, seed_company):
    """Тест удаления компании."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = test_app.delete(
        f"/api/companies/{seed_company['company_id']}",
        headers=headers
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    # Проверяем, что компания удалена
    deleted_company = await Companies.filter(company_id=seed_company["company_id"]).first()
    assert deleted_company is None


@pytest.mark.asyncio
async def test_get_companies(test_app: AsyncClient, jwt_token_admin, seed_company):
    """Тест получения списка компаний с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = test_app.get(
        "/api/companies/all",
        headers=headers
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    companies = response_data.get('companies')
    assert response_data.get('total') >= 1
    assert isinstance(companies, list)
    assert any(company["company_id"] == seed_company["company_id"]
               for company in companies)

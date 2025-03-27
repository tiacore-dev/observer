import pytest
from app.database.models import AdminUser, Company, UserRole


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_role():
    role = await UserRole.create(role_id='admin', role_name="Администратор")
    return {
        "role_id": role.role_id,
        "role_name": role.role_name
    }


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_company():
    company = await Company.create(company_name='Tiacore')
    return {
        "company_id": company.company_id,
        "company_name": company.company_name
    }


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_admin(seed_role, seed_company):
    """Добавляет тестового пользователя в базу перед тестом."""
    role = await UserRole.get(role_id=seed_role['role_id'])
    company = await Company.get(company_id=seed_company['company_id'])
    user = await AdminUser.create_admin(
        username="admin",
        password="qweasdzcx",
        role=role,
        company=company
    )
    return {
        "user_id": str(user.admin_id),
        "username": user.username,
        "role": user.role,
        "company": user.company
    }

import pytest
from app.database.models import Users, Companies, UserRoles


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_role():
    role = await UserRoles.create(role_name="Администратор")
    return {
        "role_id": str(role.role_id),
        "role_name": role.role_name
    }


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_company():
    company = await Companies.create(company_name='Tiacore')
    return {
        "company_id": str(company.company_id),
        "company_name": company.company_name
    }


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_admin():
    """Добавляет тестового пользователя в базу перед тестом."""
    user = await Users.create_user(
        username="admin",
        password="qweasdzcx"
    )
    return {
        "user_id": str(user.user_id),
        "username": user.username,
    }

import pytest
from fastapi.testclient import TestClient
from tortoise import Tortoise
from app import create_app
from app.handlers.auth_handlers import create_access_token, create_refresh_token
from config import Settings

settings = Settings()


@pytest.fixture(scope="session")
def test_app():
    """Фикстура для тестового приложения."""
    app = create_app(config_name="Test")

    client = TestClient(app)

    yield client  # Отдаём клиент тестам


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def setup_db():
    """Гарантируем, что Tortoise ORM инициализирован перед тестами."""
    await Tortoise.init(config={
        # Используем in-memory базу
        "connections": {"default": "sqlite://:memory:"},
        "apps": {
            "models": {
                "models": ["app.database.models"],
                "default_connection": "default",
            },
        },
    })
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

pytest_plugins = [
    "tests.fixtures.main_fixtures",  # Фикстуры, связанные с именами, статусами, ролями
    "tests.fixtures.prompts",
    "tests.fixtures.schedules",
    "tests.fixtures.chats"
]


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def jwt_token_admin(seed_admin):
    """Генерирует JWT токен для администратора."""
    token_data = {
        "sub": seed_admin["username"]
    }
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data)
    }

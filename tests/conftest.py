import pytest
from httpx import AsyncClient
from tortoise import Tortoise
from app import create_app
from app.handlers.auth_handlers import create_access_token, create_refresh_token
from config import Settings

settings = Settings()


@pytest.fixture
async def test_app():
    app = create_app(config_name="Test")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def setup_and_clean_db():
    await Tortoise.init(config={
        "connections": {"default": settings.TEST_DATABASE_URL},
        "apps": {
            "models": {
                "models": ["app.database.models"],
                "default_connection": "default",
            },
        },
    })
    await Tortoise.generate_schemas()

    for model in reversed(list(Tortoise.apps.get("models", {}).values())):
        try:
            await model.all().delete()
        except Exception:
            pass

    yield
    await Tortoise.close_connections()


pytest_plugins = [
    "tests.fixtures.main_fixtures",  # Фикстуры, связанные с именами, статусами, ролями
    "tests.fixtures.prompts",
    "tests.fixtures.schedules",
    "tests.fixtures.chats",
    "tests.fixtures.bots"
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

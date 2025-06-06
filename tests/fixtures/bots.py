from uuid import uuid4

import pytest

from app.database.models import Bot


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_bot():
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    bot = await Bot.create(
        id=177776,
        bot_token="test_token",
        secret_token="test_secret_token",
        bot_username="testbot",
        bot_first_name="Test",
        company_id=uuid4(),
        is_active=False,
    )

    return bot

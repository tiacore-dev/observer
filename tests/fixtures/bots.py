import pytest
from app.database.models import Bots, Companies


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_bot(seed_company):
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""
    company = await Companies.get_or_none(company_id=seed_company['company_id'])
    # Создаем юридическое лицо, передавая объекты
    bot = await Bots.create(
        bot_id=177776,
        bot_token="test_token",
        secret_token="test_secret_token",
        bot_username="testbot",
        bot_first_name="Test",
        company=company,
        is_active=False
    )

    return {
        "bot_id": bot.bot_id,
        "bot_username": bot.bot_username,
        "bot_first_name": bot.bot_first_name,
        "is_active": bot.is_active,
        "created_at": bot.created_at,
        "company_id": str(bot.company.company_id),
    }

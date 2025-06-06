import pytest

from app.database.models import Account, Chat


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_chat():
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    # Создаем юридическое лицо, передавая объекты
    chat = await Chat.create(id=1, name="Test Chat")

    return chat


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_account():
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    # Создаем юридическое лицо, передавая объекты
    account = await Account.create(name="Test Account")

    return account

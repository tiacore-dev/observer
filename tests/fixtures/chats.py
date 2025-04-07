import pytest
from app.database.models import Chats


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_chat():
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    # Создаем юридическое лицо, передавая объекты
    chat = await Chats.create(
        chat_name="Test Chat"
    )

    return {
        "chat_id": str(chat.chat_id),
        "chat_name": chat.chat_name,
        "created_at": chat.created_at,
    }

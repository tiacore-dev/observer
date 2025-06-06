from uuid import uuid4

import pytest

from app.database.models import Prompt


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_prompt():
    prompt = await Prompt.create(
        company_id=uuid4(), name="Основной", text="Проведи анализ этих сообщений"
    )

    return prompt

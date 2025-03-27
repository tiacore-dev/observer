import pytest
from app.database.models import Prompt, Company


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_prompt(seed_company):
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    # Получаем объекты из базы
    company = await Company.get_or_none(company_id=seed_company["company_id"])

    if not company:
        raise ValueError(
            "Ошибка: Не удалось получить объект company")

    # Создаем юридическое лицо, передавая объекты
    prompt = await Prompt.create(
        company=company, prompt_name="Основной", text="Проведи анализ этих сообщений"
    )

    return {
        "prompt_id": prompt.prompt_id,
        "company": prompt.company,
        "prompt_name": prompt.prompt_name,
        "text": prompt.text,
        "use_automatic": prompt.use_automatic
    }

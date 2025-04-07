import pytest
from httpx import AsyncClient
from app.database.models import Prompts


@pytest.mark.asyncio
async def test_add_prompt(test_app: AsyncClient, jwt_token_admin, seed_company):
    """Тест добавления нового промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "prompt_name": "Test Prompt",
        "text": "Содержимое тестового промпта",
        "company": seed_company['company_id']
    }

    response = test_app.post("/api/prompts/add", headers=headers, json=data)
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    prompt = await Prompts.filter(prompt_name="Test Prompt").first()

    assert prompt is not None, "Промпт не был сохранён в БД"
    assert response_data["prompt_id"] == str(prompt.prompt_id)


@pytest.mark.asyncio
async def test_edit_prompt(test_app: AsyncClient, jwt_token_admin, seed_prompt):
    """Тест редактирования промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "prompt_name": "Updated Prompt"
    }

    response = test_app.patch(
        f"/api/prompts/{seed_prompt['prompt_id']}",
        headers=headers,
        json=data
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    prompt = await Prompts.filter(prompt_id=seed_prompt['prompt_id']).first()

    assert prompt is not None, "Промпт не найден в базе"
    assert prompt.prompt_name == "Updated Prompt"


@pytest.mark.asyncio
async def test_view_prompt(test_app: AsyncClient, jwt_token_admin, seed_prompt):
    """Тест просмотра промпта по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = test_app.get(
        f"/api/prompts/{seed_prompt['prompt_id']}",
        headers=headers
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    assert response_data["prompt_id"] == str(seed_prompt["prompt_id"])
    assert response_data["prompt_name"] == seed_prompt["prompt_name"]


@pytest.mark.asyncio
async def test_delete_prompt(test_app: AsyncClient, jwt_token_admin, seed_prompt):
    """Тест удаления промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = test_app.delete(
        f"/api/prompts/{seed_prompt['prompt_id']}",
        headers=headers
    )

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    prompt = await Prompts.filter(prompt_id=seed_prompt['prompt_id']).first()
    assert prompt is None, "Промпт не был удалён из базы"


@pytest.mark.asyncio
async def test_get_prompts(test_app: AsyncClient, jwt_token_admin, seed_prompt):
    """Тест получения списка промптов с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = test_app.get(
        "/api/prompts/all",
        headers=headers
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    prompts = response_data.get('prompts')
    assert isinstance(prompts, list), "Ответ должен быть списком"
    assert response_data.get('total') > 0

    prompt_ids = [prompt["prompt_id"] for prompt in prompts]
    assert str(seed_prompt["prompt_id"]
               ) in prompt_ids, "Тестовый промпт отсутствует в списке"

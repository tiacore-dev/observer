import datetime
import pytest
from httpx import AsyncClient
from app.database.models import ChatSchedules


@pytest.mark.asyncio
async def test_add_schedule(test_app: AsyncClient, jwt_token_admin, seed_prompt, seed_chat, seed_company, seed_bot):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "prompt": seed_prompt['prompt_id'],
        "chat": seed_chat['chat_id'],
        "schedule_type": "once",
        "run_at": (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).isoformat(),
        "enabled": True,
        "time_to_send": "16:30:00",
        "send_strategy": "fixed",
        "company": str(seed_company['company_id']),
        "target_chats": [seed_chat['chat_id']],
        "bot": seed_bot['bot_id']
    }

    response = await test_app.post("/api/schedules/add", headers=headers, json=data)
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    schedule = await ChatSchedules.filter(schedule_id=response.json()["schedule_id"]).first()
    assert schedule is not None, "Расписание не сохранено в БД"


@pytest.mark.asyncio
async def test_view_schedule(test_app: AsyncClient, jwt_token_admin, seed_schedule):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get(
        f"/api/schedules/{seed_schedule['schedule_id']}", headers=headers)
    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert data["schedule_id"] == seed_schedule["schedule_id"]
    assert data["prompt"] == seed_schedule["prompt"]


@pytest.mark.asyncio
async def test_edit_schedule(test_app: AsyncClient, jwt_token_admin, seed_schedule):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "schedule_type": "daily_time",
        "time_of_day": "05:00:00",
        "enabled": False,
        "time_to_send": "05:00:00",
        "company": str(seed_schedule["company"])
    }

    response = await test_app.patch(
        f"/api/schedules/{seed_schedule['schedule_id']}",
        headers=headers,
        json=data
    )

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    schedule = await ChatSchedules.get(schedule_id=seed_schedule["schedule_id"])
    assert schedule.schedule_type == "daily_time"
    assert schedule.enabled is False


@pytest.mark.asyncio
async def test_delete_schedule(test_app: AsyncClient, jwt_token_admin, seed_schedule):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.delete(
        f"/api/schedules/{seed_schedule['schedule_id']}", headers=headers)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    schedule = await ChatSchedules.filter(schedule_id=seed_schedule["schedule_id"]).first()
    assert schedule is None, "Расписание не было удалено"


@pytest.mark.asyncio
async def test_get_schedules(test_app: AsyncClient, jwt_token_admin, seed_schedule):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/schedules/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    data = response.json()
    assert "schedules" in data
    assert data["total"] > 0

    schedule_ids = [s["schedule_id"] for s in data["schedules"]]
    assert seed_schedule["schedule_id"] in schedule_ids


@pytest.mark.asyncio
async def test_create_schedule_with_fixed_send_strategy(test_app: AsyncClient, jwt_token_admin, seed_prompt, seed_chat, seed_company, seed_bot):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "prompt": seed_prompt['prompt_id'],
        "chat": seed_chat['chat_id'],
        "schedule_type": "once",
        "run_at": (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat(),
        "enabled": True,
        "send_strategy": "fixed",
        "time_to_send": "16:30:00",
        "company": str(seed_company['company_id']),
        "target_chats": [seed_chat['chat_id']],
        "bot": seed_bot['bot_id']
    }

    response = await test_app.post("/api/schedules/add", headers=headers, json=data)
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    schedule = await ChatSchedules.get(schedule_id=response.json()["schedule_id"])
    assert schedule.send_strategy == "fixed"
    assert schedule.time_to_send.strftime("%H:%M:%S") == "16:30:00"


@pytest.mark.asyncio
async def test_create_schedule_with_relative_strategy(test_app: AsyncClient, jwt_token_admin, seed_prompt, seed_chat, seed_company, seed_bot):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "prompt": seed_prompt['prompt_id'],
        "chat": seed_chat['chat_id'],
        "schedule_type": "once",
        "run_at": (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat(),
        "enabled": True,
        "send_strategy": "relative",
        "send_after_minutes": 10,
        "company": str(seed_company['company_id']),
        "target_chats": [seed_chat['chat_id']],
        "bot": seed_bot['bot_id']
    }

    response = await test_app.post("/api/schedules/add", headers=headers, json=data)
    assert response.status_code == 201

    schedule = await ChatSchedules.get(schedule_id=response.json()["schedule_id"])
    assert schedule.send_strategy == "relative"
    assert schedule.send_after_minutes == 10


@pytest.mark.asyncio
async def test_invalid_strategy_missing_field(test_app: AsyncClient, jwt_token_admin, seed_prompt, seed_chat, seed_company, seed_bot):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "prompt": seed_prompt['prompt_id'],
        "chat": seed_chat['chat_id'],
        "schedule_type": "once",
        "run_at": (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat(),
        "enabled": True,
        "send_strategy": "fixed",  # НО time_to_send не указано!
        "company": str(seed_company['company_id']),
        "target_chats": [seed_chat['chat_id']],
        "bot": seed_bot['bot_id']
    }

    response = await test_app.post("/api/schedules/add", headers=headers, json=data)
    assert response.status_code == 422
    assert "time_to_send" in response.text

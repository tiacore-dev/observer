import datetime
import time
import pytest
from app.database.models import (
    ChatSchedules,
    TargetChats,
    Chats,
    Prompts,
    Companies,
    Bots
)


@pytest.fixture
async def seed_schedule(seed_prompt, seed_chat, seed_company, seed_bot):
    company = await Companies.get_or_none(company_id=seed_company['company_id'])
    chat = await Chats.get_or_none(chat_id=seed_chat['chat_id'])
    prompt = await Prompts.get_or_none(prompt_id=seed_prompt['prompt_id'])
    bot = await Bots.get_or_none(bot_id=seed_bot['bot_id'])
    if not company or not chat or not prompt or not bot:
        raise ValueError(
            detail="Компания, чат или промпт не найдены")
    schedule = await ChatSchedules.create(
        prompt=prompt,
        chat=chat,
        schedule_type="once",
        run_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        enabled=True,
        time_to_send=int(time.time()) + 300,
        company=company,
        bot=bot
    )

    await TargetChats.create(schedule=schedule, chat=chat)

    return {
        "schedule_id": str(schedule.schedule_id),
        "prompt": str(schedule.prompt.prompt_id),
        "chat": schedule.chat.chat_id,
        "company": str(schedule.company.company_id),
        "bot": schedule.bot.bot_id
    }

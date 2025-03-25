import secrets
import aiohttp

from fastapi import APIRouter, Request, Header, HTTPException
from pydantic import BaseModel


from config import Settings  # конфиг с URL
# твоя логика обработки апдейтов
from app.handlers.telegram_handlers import process_update
from app.database.models import BotInfo


bot_router = APIRouter(prefix="/api/bots")

settings = Settings()


class RegisterBotRequest(BaseModel):
    token: str


@bot_router.post("/register")
async def register_bot(data: RegisterBotRequest):
    try:
        bot = await validate_token_and_register(data.token)
        await set_webhook(bot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid bot token") from e
    return {"message": "Bot registered and webhook set", "bot_id": bot.bot_id}


async def validate_token_and_register(token: str) -> BotInfo:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/bot{token}/getMe") as resp:
            data = await resp.json()
            if not data.get("ok"):
                raise ValueError("Invalid token")
            bot_info = data["result"]

    bot_id = bot_info["id"]
    username = bot_info["username"]

    secret = secrets.token_hex(16)  # для валидации входящих запросов

    bot = await BotInfo.create(
        bot_id=bot_id,
        name=username,
        token=token,
        secret_token=secret
    )

    return bot


async def set_webhook(bot: BotInfo):
    url = f"https://api.telegram.org/bot{bot.token}/setWebhook"
    payload = {
        "url": f"{settings.WEBHOOK_BASE_URL}/webhook",
        "secret_token": bot.secret_token,
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)


@bot_router.post("/webhook")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    if not x_telegram_bot_api_secret_token:
        raise HTTPException(status_code=403, detail="Missing secret token")

    bot = await BotInfo.get_or_none(secret_token=x_telegram_bot_api_secret_token)
    if not bot:
        raise HTTPException(status_code=403, detail="Unknown bot")

    payload = await request.json()
    await process_update(bot, payload)
    return {"ok": True}

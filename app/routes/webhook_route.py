from fastapi import APIRouter,  Header, HTTPException, Depends, status, Request
from fastapi.responses import Response
from loguru import logger
from app.handlers.telegram_api_url_handlers import (
    delete_webhook,
    get_webhook_info,
    set_webhook
)
from app.handlers.telegram_handlers import process_update
from app.handlers.auth_handlers import get_current_user
from app.database.models import Bots, Users
from app.exceptions.telegram import TelegramAPIError

webhook_router = APIRouter()


@webhook_router.patch("/{bot_id}/set",
                      status_code=status.HTTP_204_NO_CONTENT)
async def set_bot_webhook(bot_id: int, user: Users = Depends(get_current_user)):
    bot = await Bots.get_or_none(bot_id=bot_id)

    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")

    try:
        await set_webhook(bot)
    except TelegramAPIError as e:
        logger.error(f"Не удалось установить webhook: {e}")
        raise HTTPException(
            status_code=502, detail="Ошибка Telegram API") from e

    bot.is_active = True
    await bot.save()


@webhook_router.delete("/{bot_id}/delete",
                       status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot_webhook(bot_id: int, user: Users = Depends(get_current_user)):
    bot = await Bots.get_or_none(bot_id=bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    try:
        await delete_webhook(bot.bot_token)
    except TelegramAPIError as e:
        logger.error(f"Не удалось удалить webhook: {e}")
        raise HTTPException(
            status_code=502, detail="Ошибка Telegram API") from e
    bot.is_active = False
    await bot.save()


@webhook_router.get("/{bot_id}/info")
async def get_bot_webhook_info(bot_id: int, user: Users = Depends(get_current_user)):
    bot = await Bots.get_or_none(bot_id=bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")

    try:
        return await get_webhook_info(bot.bot_token)
    except TelegramAPIError as e:
        logger.error(f"Не удалось получить информацию о webhook: {e}")
        raise HTTPException(
            status_code=502, detail="Ошибка Telegram API") from e


@webhook_router.post("/updates", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None),
):
    try:
        data = await request.json()
        logger.debug(f"📦 Parsed JSON: {data}")
        bot = await Bots.get_or_none(
            secret_token=x_telegram_bot_api_secret_token).prefetch_related("company")
        if not bot:
            logger.warning("⛔ Неверный токен")
            raise HTTPException(status_code=403, detail="Invalid secret token")
        await process_update(data, bot)
    except Exception as e:
        logger.exception(f"❌ Ошибка в webhook: {e}")

    return Response(status_code=200)

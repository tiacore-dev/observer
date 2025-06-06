from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import Response
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.dependency_handler import require_permission_in_context

from app.database.models import Bot
from app.exceptions.telegram import TelegramAPIError
from app.handlers.telegram_api_url_handlers import (
    delete_webhook,
    get_webhook_info,
    set_webhook,
)
from app.handlers.telegram_handler import process_update

webhook_router = APIRouter()


@webhook_router.patch("/{bot_id}/set", status_code=status.HTTP_204_NO_CONTENT)
async def set_bot_webhook(
    bot_id: int,
    _=Depends(require_permission_in_context("set_webhook")),
    settings=Depends(get_settings),
):
    bot = await Bot.get_or_none(id=bot_id)

    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")

    try:
        await set_webhook(bot, settings)
    except TelegramAPIError as e:
        logger.error(f"Не удалось установить webhook: {e}")
        raise HTTPException(status_code=502, detail="Ошибка Telegram API") from e

    bot.is_active = True
    await bot.save()


@webhook_router.delete("/{bot_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot_webhook(
    bot_id: int, _=Depends(require_permission_in_context("delete_webhook"))
):
    bot = await Bot.get_or_none(id=bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    try:
        await delete_webhook(bot.bot_token)
    except TelegramAPIError as e:
        logger.error(f"Не удалось удалить webhook: {e}")
        raise HTTPException(status_code=502, detail="Ошибка Telegram API") from e
    bot.is_active = False
    await bot.save()


@webhook_router.get("/{bot_id}/info")
async def get_bot_webhook_info(
    bot_id: int, _=Depends(require_permission_in_context("view_webhook_info"))
):
    bot = await Bot.get_or_none(id=bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")

    try:
        return await get_webhook_info(bot.bot_token)
    except TelegramAPIError as e:
        logger.error(f"Не удалось получить информацию о webhook: {e}")
        raise HTTPException(status_code=502, detail="Ошибка Telegram API") from e


@webhook_router.post("/updates", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None),
    settings=Depends(get_settings),
):
    try:
        data = await request.json()
        logger.debug(f"📦 Parsed JSON: {data}")
        bot = await Bot.get_or_none(
            secret_token=x_telegram_bot_api_secret_token
        ).prefetch_related("company")
        if not bot:
            logger.warning("⛔ Неверный токен")
            raise HTTPException(status_code=403, detail="Invalid secret token")
        await process_update(data, bot, settings)
    except Exception as e:
        logger.exception(f"❌ Ошибка в webhook: {e}")

    return Response(status_code=200)

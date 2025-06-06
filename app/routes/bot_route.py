from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Bot
from app.handlers.telegram_api_url_handlers import (
    delete_webhook,
    validate_token_and_register,
)
from app.pydantic_models.bot_schemas import (
    BotListSchema,
    BotSchema,
    RegisterBotRequest,
    bot_filter_params,
)

bot_router = APIRouter()


@bot_router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_bot(
    data: RegisterBotRequest = Body(...),
    context=Depends(require_permission_in_context("add_bot")),
):
    try:
        bot = await validate_token_and_register(
            data.token, data.company_id, data.comment
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid bot token") from e
    return {"bot_id": bot.id}


@bot_router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: int, _=Depends(require_permission_in_context("delete_bot"))
):
    try:
        bot = await Bot.filter(id=bot_id).first()
        if not bot:
            logger.warning(f"Бот {bot_id} не найден")
            raise HTTPException(status_code=404, detail="Бот не найден")

        token = bot.bot_token
        await bot.delete()

        await delete_webhook(token)
        logger.success(f"Бот {bot_id} успешно удален")

    except Exception as e:
        logger.exception("Ошибка при удалении бота")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@bot_router.get(
    "/all", response_model=BotListSchema, summary="Получение списка ботов с фильтрацией"
)
async def get_bots(
    filters: dict = Depends(bot_filter_params),
    _=Depends(require_permission_in_context("get_all_bots")),
):
    logger.info(f"Запрос на список ботов: {filters}")

    try:
        query = Q()

        if filters.get("company_id"):
            query &= Q(company_id=filters["company_id"])

        if filters.get("bot_username"):
            query &= Q(bot_username__icontains=filters["bot_username"])
        if filters.get("bot_first_name"):
            query &= Q(bot_first_name__icontains=filters["bot_first_name"])

        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
            filters.get('sort_by', 'bot_username')
        }"
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        total_count = await Bot.filter(query).count()

        bots = (
            await Bot.filter(query)
            .order_by(order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .values(
                "id",
                "bot_token",
                "bot_username",
                "bot_first_name",
                "company_id",
                "is_active",
                "created_at",
                "comment",
            )
        )

        return BotListSchema(
            total=total_count,
            bots=[BotSchema(**bot) for bot in bots],
        )

    except Exception as e:
        logger.exception("Ошибка при получении списка ботов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@bot_router.get("/{bot_id}", response_model=BotSchema, summary="Просмотр промпта")
async def get_bot(
    bot_id: int = Path(
        ..., title="ID промпта", description="ID просматриваемого промпта"
    ),
    _=Depends(require_permission_in_context("view_bot")),
):
    logger.info(f"Запрос на просмотр промпта: {bot_id}")
    try:
        bot = (
            await Bot.filter(id=bot_id)
            .first()
            .values(
                "id",
                "bot_token",
                "bot_username",
                "bot_first_name",
                "company_id",
                "is_active",
                "created_at",
                "comment",
            )
        )

        if bot is None:
            logger.warning(f"Промпт {bot_id} не найден")
            raise HTTPException(status_code=404, detail="Промпт не найден")

        bot_schema = BotSchema(**bot)

        logger.success(f"Промпт найден: {bot_schema}")
        return bot_schema
    except Exception as e:
        logger.exception("Ошибка при просмотре промпта")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e

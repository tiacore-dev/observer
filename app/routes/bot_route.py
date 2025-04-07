from fastapi import APIRouter, HTTPException, Depends, status, Path, Body
from loguru import logger
from tortoise.expressions import Q
from app.handlers.telegram_api_url_handlers import validate_token_and_register, delete_webhook
from app.handlers.auth_handlers import get_current_user
from app.database.models import Users, Bots
from app.pydantic_models.bot_schemas import RegisterBotRequest, BotSchema, BotListSchema, bot_filter_params

bot_router = APIRouter()


@bot_router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_bot(data: RegisterBotRequest = Body(...), user: Users = Depends(get_current_user)):
    try:
        bot = await validate_token_and_register(data.token, data.company)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid bot token") from e
    return {"bot_id": bot.bot_id}


@bot_router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(bot_id: int, user: Users = Depends(get_current_user)):
    try:
        bot = await Bots.filter(bot_id=bot_id).first()
        if not bot:
            logger.warning(f"Бот {bot_id} не найден")
            raise HTTPException(status_code=404, detail="Бот не найден")

        token = bot.bot_token
        await bot.delete()  # <-- await обязательно!

        await delete_webhook(token)
        logger.success(f"Бот {bot_id} успешно удален")

    except Exception as e:
        logger.exception("Ошибка при удалении бота")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@bot_router.get("/all", response_model=BotListSchema, summary="Получение списка ботов с фильтрацией")
async def get_bots(
    filters: dict = Depends(bot_filter_params),
    user: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на список ботов: {filters}")

    try:
        query = Q()

        if filters.get("company"):
            query &= Q(company=filters["company"])

        if filters.get("search"):
            query &= Q(bot_username__icontains=filters["search"])

        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{filters.get('sort_by', 'bot_username')}"
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        total_count = await Bots.filter(query).count()

        bots = await Bots.filter(query).order_by(order_by).offset(
            (page - 1) * page_size
        ).limit(page_size).values(
            "bot_id",
            "bot_token",
            "bot_username",
            "bot_first_name",
            "company_id",
            "is_active",
            "created_at"
        )

        return BotListSchema(
            total=total_count,
            bots=[
                BotSchema(
                    bot_id=bot["bot_id"],
                    bot_token=bot["bot_token"],
                    bot_username=bot["bot_username"],
                    bot_first_name=bot["bot_first_name"],
                    company=bot["company_id"],
                    is_active=bot["is_active"],
                    created_at=bot["created_at"]
                )
                for bot in bots
            ]
        )

    except Exception as e:
        logger.exception("Ошибка при получении списка ботов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@bot_router.get("/{bot_id}", response_model=BotSchema, summary="Просмотр промпта")
async def get_bot(
    bot_id: int = Path(..., title="ID промпта",
                       description="ID просматриваемого промпта"),
    user: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на просмотр промпта: {bot_id}")
    try:
        bot = await Bots.filter(bot_id=bot_id).first().values(
            "bot_id",
            "bot_token",
            "bot_username",
            "bot_first_name",
            "company_id",
            "is_active",
            "created_at"
        )

        if bot is None:
            logger.warning(f"Промпт {bot_id} не найден")
            raise HTTPException(status_code=404, detail="Промпт не найден")

        bot_schema = BotSchema(
            bot_id=bot["bot_id"],
            bot_token=bot["bot_token"],
            bot_username=bot["bot_username"],
            bot_first_name=bot["bot_first_name"],
            company=bot["company_id"],
            is_active=bot["is_active"],
            created_at=bot["created_at"]
        )

        logger.success(f"Промпт найден: {bot_schema}")
        return bot_schema
    except Exception as e:
        logger.exception("Ошибка при просмотре промпта")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e

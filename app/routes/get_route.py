from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Account, Chat
from app.pydantic_models.get_schemas import (
    AccountListSchema,
    AccountSchema,
    ChatListSchema,
    ChatSchema,
    account_filter_params,
    chat_filter_params,
)

get_router = APIRouter()


# 📌 Обновленные эндпоинты с `PaginatedResponse`
@get_router.get(
    "/chats/all", response_model=ChatListSchema, summary="Получение списка чатов"
)
async def get_chats(
    filters: dict = Depends(chat_filter_params),
    _=Depends(require_permission_in_context("get_all_chats")),
):
    try:
        query = Chat.all()

        if filters.get("chat_name"):
            query = query.filter(Q(name__icontains=filters["chat_name"]))
        if filters.get("bot_id"):
            query = query.filter(bot_relations__bot_id=filters["bot_id"])
        # 🛠️ Маппинг внешнего поля на поле в БД
        sort_field_map = {"chat_name": "name", "created_at": "created_at"}
        sort_by = sort_field_map.get(filters["sort_by"], filters["sort_by"])
        order_by = f"{'-' if filters['order'] == 'desc' else ''}{sort_by}"
        query = query.order_by(order_by)

        total = await query.count()
        results = (
            await query.offset((filters["page"] - 1) * filters["page_size"])
            .limit(filters["page_size"])
            .values("id", "name", "created_at")
        )

        # 🚀 Благодаря alias'ам и populate_by_name — работает из коробки
        return ChatListSchema(
            total=total,
            chats=[ChatSchema(**chat) for chat in results],
        )
    except Exception as e:
        logger.exception("Ошибка при получении списка чатов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@get_router.get(
    "/accounts/all",
    response_model=AccountListSchema,
    summary="Получение списка аккаунтов",
)
async def get_accounts(
    filters: dict = Depends(account_filter_params),
    _=Depends(require_permission_in_context("get_all_accounts")),
):
    try:
        query = Account.all()

        if filters.get("username"):
            query = query.filter(Q(username__icontains=filters["username"]))

        # 👇 Маппинг алиасов во внутренние имена полей модели
        sort_field_map = {
            "account_name": "name",
            "username": "username",
            "created_at": "created_at",
        }
        sort_by = sort_field_map.get(filters["sort_by"], filters["sort_by"])
        order_by = f"{'-' if filters['order'] == 'desc' else ''}{sort_by}"
        query = query.order_by(order_by)

        total = await query.count()
        results = (
            await query.offset((filters["page"] - 1) * filters["page_size"])
            .limit(filters["page_size"])
            .values("id", "name", "username", "created_at")
        )

        return AccountListSchema(
            total=total,
            accounts=[AccountSchema(**acc) for acc in results],
        )
    except Exception as e:
        logger.exception("Ошибка при получении списка аккаунтов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e

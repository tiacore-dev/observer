from fastapi import APIRouter, Depends, HTTPException
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Account, AccountCompanyRelation, Bot, Chat
from app.pydantic_models.get_schemas import (
    AccountListSchema,
    AccountSchema,
    ChatListSchema,
    ChatSchema,
    account_filter_params,
    chat_filter_params,
)

get_router = APIRouter()


@get_router.get(
    "/chats/all", response_model=ChatListSchema, summary="Получение списка чатов"
)
async def get_chats(
    filters: dict = Depends(chat_filter_params),
    context=Depends(require_permission_in_context("get_all_chats")),
):
    # Начинаем с чатов, но будем фильтровать по связи с ботами
    query = Chat.filter(bot_relations__bot__isnull=False)

    # 🔐 Фильтрация по company_id (через бота)
    if not context["is_superadmin"]:
        company_id = context.get("company_id")
        if not company_id:
            return ChatListSchema(total=0, chats=[])

        query = query.filter(bot_relations__bot__company_id=company_id)

        # Защита от доступа к чужим ботам через фильтр
        if filters.get("bot_id"):
            bot = await Bot.filter(id=filters["bot_id"]).first()
            if not bot or bot.company_id != company_id:
                raise HTTPException(status_code=403, detail="Нет доступа к этому боту")

    # 👁 Фильтр по имени
    if filters.get("chat_name"):
        query = query.filter(Q(name__icontains=filters["chat_name"]))

    # 🔁 Фильтр по конкретному боту
    if filters.get("bot_id"):
        query = query.filter(bot_relations__bot_id=filters["bot_id"])

    # 🧭 Сортировка
    sort_field_map = {"chat_name": "name", "created_at": "created_at"}
    requested_sort_by = filters.get("sort_by") or "created_at"
    sort_by = sort_field_map.get(requested_sort_by, requested_sort_by)

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{sort_by}"
    query = query.order_by(order_by)

    # 📊 Пагинация
    total = await query.count()
    results = (
        await query.offset((filters["page"] - 1) * filters["page_size"])
        .limit(filters["page_size"])
        .distinct()  # 💡 на случай дубликатов из-за join
        .values("id", "name", "created_at")
    )

    return ChatListSchema(
        total=total,
        chats=[ChatSchema(**chat) for chat in results],
    )


@get_router.get(
    "/accounts/all",
    response_model=AccountListSchema,
    summary="Получение списка аккаунтов",
)
async def get_accounts(
    filters: dict = Depends(account_filter_params),
    context=Depends(require_permission_in_context("get_all_accounts")),
):
    query = Account.all()
    # 🔒 Фильтрация по company_id через релейшн
    if not context["is_superadmin"]:
        if context.get("company_id"):
            account_ids = await AccountCompanyRelation.filter(
                company_id=context["company_id"]
            ).values_list("account_id", flat=True)

            if not account_ids:
                return AccountListSchema(total=0, accounts=[])

            query = query.filter(id__in=account_ids)
        else:
            return AccountListSchema(total=0, accounts=[])

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

from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q
from loguru import logger
from app.handlers.auth_handlers import get_current_user
from app.database.models import Chats, Accounts, UserRoles, Permissions
from app.pydantic_models.get_schemas import (
    ChatListSchema,
    ChatSchema,
    chat_filter_params,
    AccountListSchema,
    AccountSchema,
    account_filter_params,
    UserRoleListSchema,
    UserRoleSchema,
    user_role_filter_params,
    PermissionListSchema,
    PermissionSchema,
    permission_filter_params

)

get_router = APIRouter()


# 📌 Обновленные эндпоинты с `PaginatedResponse`
@get_router.get(
    "/chats/all",
    response_model=ChatListSchema,
    summary="Получение списка чатов"
)
async def get_chats(filters: dict = Depends(chat_filter_params), user: str = Depends(get_current_user)):
    try:
        query = Chats.all()

        if filters.get("chat_name"):
            query = query.filter(Q(chat_name__icontains=filters["chat_name"]))

        order_by = f"{'-' if filters['order'] == 'desc' else ''}{filters['sort_by']}"
        query = query.order_by(order_by)

        total = await query.count()
        results = await query.offset((filters['page'] - 1) * filters['page_size']).limit(filters['page_size'])

        return ChatListSchema(
            total=total,
            chats=[
                ChatSchema(
                    chat_id=chat.chat_id,
                    chat_name=chat.chat_name or "",
                    created_at=chat.created_at
                ) for chat in results
            ]
        )
    except Exception as e:
        logger.exception("Ошибка при получении списка чатов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@get_router.get(
    "/accounts/all",
    response_model=AccountListSchema,
    summary="Получение списка аккаунтов"
)
async def get_accounts(filters: dict = Depends(account_filter_params), user: str = Depends(get_current_user)):
    try:
        query = Accounts.all()

        if filters.get("username"):
            query = query.filter(Q(username__icontains=filters["username"]))

        order_by = f"{'-' if filters['order'] == 'desc' else ''}{filters['sort_by']}"
        query = query.order_by(order_by)

        total = await query.count()
        results = await query.offset((filters['page'] - 1) * filters['page_size']).limit(filters['page_size'])

        return AccountListSchema(
            total=total,
            accounts=[
                AccountSchema(
                    account_id=acc.account_id,
                    username=acc.username or "",
                    account_name=acc.account_name or "",
                    created_at=acc.created_at
                ) for acc in results
            ]
        )
    except Exception as e:
        logger.exception("Ошибка при получении списка аккаунтов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@get_router.get(
    "/user-roles/all",
    response_model=UserRoleListSchema,
    summary="Получение списка ролей пользователей"
)
async def get_user_roles(filters: dict = Depends(user_role_filter_params), user: str = Depends(get_current_user)):
    try:
        query = UserRoles.all()

        if filters.get("role_name"):
            query = query.filter(Q(role_name__icontains=filters["role_name"]))

        order_by = f"{'-' if filters['order'] == 'desc' else ''}{filters['sort_by']}"
        query = query.order_by(order_by)

        total = await query.count()
        results = await query.offset((filters['page'] - 1) * filters['page_size']).limit(filters['page_size'])

        return UserRoleListSchema(
            total=total,
            roles=[
                UserRoleSchema(
                    role_id=role.role_id,
                    role_name=role.role_name
                ) for role in results
            ]
        )
    except Exception as e:
        logger.exception("Ошибка при получении списка ролей пользователей")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@get_router.get(
    "/permissions/all",
    response_model=PermissionListSchema,
    summary="Получение списка разрешений (Permissions)"
)
async def get_permissions(filters: dict = Depends(permission_filter_params), user: str = Depends(get_current_user)):
    try:
        query = Permissions.all()

        if filters.get("permission_name"):
            query = query.filter(
                permission_name__icontains=filters["permission_name"])

        order_by = f"{'-' if filters['order'] == 'desc' else ''}{filters['sort_by']}"
        query = query.order_by(order_by)

        total = await query.count()
        permissions = await query.offset((filters["page"] - 1) * filters["page_size"]).limit(filters["page_size"])

        return PermissionListSchema(
            total=total,
            permissions=[
                PermissionSchema(
                    permission_id=permission.permission_id,
                    comment=permission.comment,
                    permission_name=permission.permission_name
                ) for permission in permissions
            ]
        )

    except Exception as e:
        logger.exception("Ошибка при получении списка разрешений")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e

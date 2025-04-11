import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4
from fastapi import Query


class ChatSchema(BaseModel):
    chat_id: int
    chat_name: str
    created_at: datetime.datetime


class ChatListSchema(BaseModel):
    total: int
    chats: List[ChatSchema]


def chat_filter_params(
    chat_name: Optional[str] = Query(
        None, description="Фильтр по названию бота"),
    sort_by: Optional[str] = Query(
        "chat_name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "chat_name": chat_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }


class AccountSchema(BaseModel):
    account_id: int
    account_name: str
    username: str
    created_at: datetime.datetime


class AccountListSchema(BaseModel):
    total: int
    accounts: List[AccountSchema]


def account_filter_params(
    username: Optional[str] = Query(
        None, description="Фильтр по названию чата"),
    sort_by: Optional[str] = Query(
        "username", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "username": username,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }


class UserRoleSchema(BaseModel):
    role_id: UUID4
    role_name: str


class UserRoleListSchema(BaseModel):
    total: int
    roles: List[UserRoleSchema]


def user_role_filter_params(
    role_name: Optional[str] = Query(
        None, description="Фильтр по названию чата"),
    sort_by: Optional[str] = Query(
        "role_name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "role_name": role_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }


class PermissionSchema(BaseModel):
    permission_id: UUID4
    role_id: UUID4
    role_name: str


class PermissionListSchema(BaseModel):
    total: int
    permissions: List[PermissionSchema]


def permission_filter_params(
    role_name: Optional[str] = Query(
        None, description="Фильтр по названию роли"),
    sort_by: Optional[str] = Query(
        "role__role_name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "role_name": role_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

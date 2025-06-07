import datetime
from typing import List, Optional

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class ChatSchema(CleanableBaseModel):
    id: int = Field(..., alias="chat_id")
    name: str = Field(..., alias="chat_name")
    created_at: datetime.datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ChatListSchema(CleanableBaseModel):
    total: int
    chats: List[ChatSchema]


def chat_filter_params(
    chat_name: Optional[str] = Query(None, description="Фильтр по названию бота"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "chat_name": chat_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }


class AccountSchema(CleanableBaseModel):
    id: int = Field(..., alias="account_id")
    name: str = Field(..., alias="account_name")
    username: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class AccountListSchema(CleanableBaseModel):
    total: int
    accounts: List[AccountSchema]


def account_filter_params(
    username: Optional[str] = Query(None, description="Фильтр по названию чата"),
    sort_by: Optional[str] = Query("username", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "username": username,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

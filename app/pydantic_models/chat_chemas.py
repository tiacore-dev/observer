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
    search: Optional[str] = Query(
        None, description="Фильтр по названию бота"),
    company: Optional[UUID4] = Query(None),
    sort_by: Optional[str] = Query(
        "chat_username", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "search": search,
        "company": company,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }

import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4, Field
from fastapi import Query


class RegisterBotRequest(BaseModel):
    token: str = Field(...)
    company: UUID4 = Field(...)


class BotResponseModel(BaseModel):
    bot_id: int


class BotSchema(BaseModel):
    bot_id: int
    bot_token: str
    bot_username: str
    bot_first_name: str
    company: UUID4
    is_active: bool
    created_at: datetime.datetime


class BotListSchema(BaseModel):
    total: int
    bots: List[BotSchema]


def bot_filter_params(
    search: Optional[str] = Query(
        None, description="Фильтр по названию бота"),
    company: Optional[UUID4] = Query(None),
    sort_by: Optional[str] = Query(
        "bot_username", description="Поле сортировки"),
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

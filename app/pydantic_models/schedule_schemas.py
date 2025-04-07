from typing import Optional, List
import datetime
from pydantic import BaseModel, Field, UUID4
from fastapi import Query


class ScheduleCreateSchema(BaseModel):
    chat: int = Field(...)
    prompt: UUID4 = Field(...)
    schedule_type: str = Field(...)

    interval_hours: Optional[int] = Field(None)
    interval_minutes: Optional[int] = Field(None)
    time_of_day: Optional[datetime.time] = Field(None)
    cron_expression: Optional[str] = Field(None)
    run_at: Optional[datetime.datetime] = Field(None)

    target_chats: List[int] = Field(...)

    enabled: Optional[bool] = True
    time_to_send: int = Field(...)
    company: UUID4 = Field(...)


class ScheduleEditSchema(BaseModel):
    chat: Optional[int] = Field(None)
    prompt: Optional[UUID4] = Field(None)
    schedule_type: Optional[str] = Field(None)

    interval_hours: Optional[int] = Field(None)
    interval_minutes: Optional[int] = Field(None)
    time_of_day: Optional[datetime.time] = Field(None)
    cron_expression: Optional[str] = Field(None)
    run_at: Optional[datetime.datetime] = Field(None)

    target_chats: Optional[List[int]] = Field(None)
    removed_chats: Optional[List[int]] = Field(None)

    enabled: Optional[bool] = Field(None)
    time_to_send: Optional[int] = Field(None)
    company: Optional[UUID4] = Field(None)


class ScheduleSchema(BaseModel):
    schedule_id: UUID4
    chat: int
    prompt: UUID4
    company: UUID4
    schedule_type: str

    interval_hours: Optional[int]
    interval_minutes: Optional[int]
    time_of_day: Optional[datetime.time]
    cron_expression: Optional[str]
    run_at: Optional[datetime.datetime]

    enabled: bool
    last_run_at: Optional[datetime.datetime]
    created_at: datetime.datetime
    time_to_send: int

    target_chats: list[int]


class ScheduleShortSchema(BaseModel):
    schedule_id: UUID4
    prompt: UUID4
    schedule_type: str
    enabled: bool
    company: UUID4
    chat: int
    created_at: datetime.datetime


class ScheduleListSchema(BaseModel):
    total: int
    schedules: List[ScheduleShortSchema]


class ScheduleResponseSchema(BaseModel):
    schedule_id: UUID4


def schedule_filter_params(
    search: Optional[str] = Query(
        None, description="Фильтр по названию промпта"),
    company: Optional[UUID4] = Query(None),
    chat: Optional[UUID4] = Query(None),
    schedule_type: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query(
        "schedule_type", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "search": search,
        "company": company,
        "chat": chat,
        "schedule_type": schedule_type,
        "enabled": enabled,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }

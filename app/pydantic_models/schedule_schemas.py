import datetime
from typing import List, Literal, Optional
from uuid import UUID

from apscheduler.triggers.cron import CronTrigger
from fastapi import Query
from pydantic import Field, field_validator, model_validator
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class ScheduleCreateSchema(CleanableBaseModel):
    chat_id: int = Field(...)
    prompt_id: UUID = Field(...)
    schedule_type: str = Field(...)
    message_intro: Optional[str] = Field(None)

    interval_hours: Optional[int] = Field(None)
    interval_minutes: Optional[int] = Field(None)
    time_of_day: Optional[datetime.time] = Field(None)
    cron_expression: Optional[str] = Field(None)
    run_at: Optional[datetime.datetime] = Field(None)

    company_id: UUID = Field(...)
    target_chats: List[int] = Field(...)
    bot_id: int = Field(...)
    enabled: Optional[bool] = True

    send_strategy: Literal["fixed", "relative"] = Field(
        ...,
        description="fixed — в указанное время, relative — через X минут после анализа",
    )
    time_to_send: Optional[datetime.time] = Field(None)
    send_after_minutes: Optional[int] = Field(None)

    @field_validator("cron_expression")
    @classmethod
    def validate_cron_expression(cls, value):
        if value:
            try:
                CronTrigger.from_crontab(value)
            except Exception as e:
                raise ValueError(f"Некорректное cron-выражение: {e}") from e
        return value

    @model_validator(mode="after")
    def validate_required_fields(self):
        # Валидация типа расписания
        match self.schedule_type:
            case "interval":
                if self.interval_hours is None and self.interval_minutes is None:
                    raise ValueError(
                        """Для типа interval необходимо указать 
                        interval_hours или interval_minutes"""
                    )
            case "daily_time":
                if self.time_of_day is None:
                    raise ValueError("Для типа daily_time необходимо указать time_of_day")
            case "cron":
                if self.cron_expression is None:
                    raise ValueError("Для типа cron необходимо указать cron_expression")
            case "once":
                if self.run_at is None:
                    raise ValueError("Для типа once необходимо указать run_at")

        # Валидация стратегии отправки
        if self.send_strategy == "fixed" and not self.time_to_send:
            raise ValueError("Для стратегии 'fixed' необходимо указать time_to_send")

        if self.send_strategy == "relative" and self.send_after_minutes is None:
            raise ValueError("Для стратегии 'relative' необходимо указать send_after_minutes")

        return self


class ScheduleEditSchema(CleanableBaseModel):
    chat_id: Optional[int] = Field(None)
    prompt_id: Optional[UUID] = Field(None)
    schedule_type: Optional[str] = Field(None)
    message_intro: Optional[str] = Field(None)

    interval_hours: Optional[int] = Field(None)
    interval_minutes: Optional[int] = Field(None)
    time_of_day: Optional[datetime.time] = Field(None)
    cron_expression: Optional[str] = Field(None)
    run_at: Optional[datetime.datetime] = Field(None)

    target_chats: Optional[List[int]] = Field(None)
    removed_chats: Optional[List[int]] = Field(None)
    bot_id: Optional[int] = Field(None)
    enabled: Optional[bool] = Field(None)

    send_strategy: Optional[Literal["fixed", "relative"]] = Field(None)
    time_to_send: Optional[datetime.time] = Field(None)
    send_after_minutes: Optional[int] = Field(None)

    company_id: Optional[UUID] = Field(None)

    @field_validator("cron_expression")
    @classmethod
    def validate_cron_expression(cls, value):
        if value:
            try:
                CronTrigger.from_crontab(value)
            except Exception as e:
                raise ValueError(f"Некорректное cron-выражение: {e}") from e
        return value

    @model_validator(mode="after")
    def validate_schedule_edit(self):
        # Тип расписания
        if self.schedule_type == "interval" and not (self.interval_hours or self.interval_minutes):
            raise ValueError("Для типа interval нужно указать interval_hours или interval_minutes")

        if self.schedule_type == "daily_time" and not self.time_of_day:
            raise ValueError("Для типа daily_time нужно указать time_of_day")

        if self.schedule_type == "cron" and not self.cron_expression:
            raise ValueError("Для типа cron нужно указать cron_expression")

        if self.schedule_type == "once" and not self.run_at:
            raise ValueError("Для типа once нужно указать run_at")

        # Стратегия отправки
        if self.send_strategy == "fixed" and not self.time_to_send:
            raise ValueError("Для стратегии 'fixed' необходимо указать time_to_send")

        if self.send_strategy == "relative" and self.send_after_minutes is None:
            raise ValueError("Для стратегии 'relative' необходимо указать send_after_minutes")

        return self


class ScheduleSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="schedule_id")
    chat_id: int
    prompt_id: UUID
    company_id: UUID
    schedule_type: str
    message_intro: Optional[str] = Field(None)

    interval_hours: Optional[int] = None
    interval_minutes: Optional[int] = None
    time_of_day: Optional[datetime.time] = None
    cron_expression: Optional[str] = None
    run_at: Optional[datetime.datetime] = None

    enabled: bool
    last_run_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    send_strategy: str
    time_to_send: Optional[datetime.time] = None
    send_after_minutes: Optional[int] = None

    bot_id: int

    target_chats: list[int]

    class Config:
        from_attributes = True
        populate_by_name = True


class ScheduleShortSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="schedule_id")
    prompt_id: UUID
    schedule_type: str
    enabled: bool
    company_id: UUID
    chat_id: int
    created_at: datetime.datetime
    bot_id: int

    class Config:
        from_attributes = True
        populate_by_name = True


class ScheduleListSchema(CleanableBaseModel):
    total: int
    schedules: List[ScheduleShortSchema]


class ScheduleResponseSchema(CleanableBaseModel):
    schedule_id: UUID


def schedule_filter_params(
    company_id: Optional[UUID] = Query(None),
    chat_id: Optional[UUID] = Query(None),
    schedule_type: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("schedule_type", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "company": company_id,
        "chat": chat_id,
        "schedule_type": schedule_type,
        "enabled": enabled,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

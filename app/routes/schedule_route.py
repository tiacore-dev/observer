from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import (
    Bot,
    Chat,
    ChatSchedule,
    Prompt,
    TargetChat,
)
from app.handlers.rabbit_handler import publish_schedule_event
from app.pydantic_models.schedule_schemas import (
    ScheduleCreateSchema,
    ScheduleEditSchema,
    ScheduleListSchema,
    ScheduleResponseSchema,
    ScheduleSchema,
    ScheduleShortSchema,
    schedule_filter_params,
)
from app.scheduler.scheduler import list_scheduled_jobs
from app.utils.validate_helpers import validate_exists

schedule_router = APIRouter()


@schedule_router.post(
    "/add", response_model=ScheduleResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_schedule(
    data: ScheduleCreateSchema = Body(...),
    _=Depends(require_permission_in_context("add_schedule")),
    settings=Depends(get_settings),
):
    await validate_exists(Chat, data.chat_id, "Чат")
    await validate_exists(Bot, data.bot_id, "Бот")
    await validate_exists(Prompt, data.prompt_id, "Промпт")

    try:
        schedule = await ChatSchedule.create(**data.model_dump(exclude_unset=True))

        if data.target_chats:
            for chat_id in data.target_chats:
                await TargetChat.create(schedule=schedule, chat_id=chat_id)
        await publish_schedule_event(schedule.id, settings=settings, action="add")

        return ScheduleResponseSchema(schedule_id=schedule.id)

    except Exception as e:
        logger.exception(f"Ошибка при создании расписания: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@schedule_router.patch("/{schedule_id}/toggle", status_code=status.HTTP_204_NO_CONTENT)
async def toggle_schedule(
    schedule_id: UUID,
    _=Depends(require_permission_in_context("toggle_schedule")),
    settings=Depends(get_settings),
):
    schedule = await ChatSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")

    schedule.enabled = not schedule.enabled
    await schedule.save()
    if schedule.enabled:
        await publish_schedule_event(schedule_id, settings=settings, action="add")
    else:
        await publish_schedule_event(schedule_id, settings=settings, action="delete")


@schedule_router.patch("/{schedule_id}", response_model=ScheduleResponseSchema)
async def edit_schedule(
    schedule_id: UUID,
    data: ScheduleEditSchema = Body(...),
    _=Depends(require_permission_in_context("edit_schedule")),
    settings=Depends(get_settings),
):
    updated_data = data.model_dump(exclude_unset=True)
    schedule = await ChatSchedule.get_or_none(id=schedule_id)
    if not schedule:
        logger.warning(f"Расписание {schedule_id} не найдено")
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    await publish_schedule_event(schedule_id, settings=settings, action="delete")
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")

    if "chat" in updated_data:
        await validate_exists(Chat, data.chat_id, "Чат")

    if "prompt" in updated_data:
        await validate_exists(Prompt, data.prompt_id, "Промпт")

    if "bot" in updated_data:
        await validate_exists(Bot, data.bot_id, "Бот")

    await schedule.update_from_dict(updated_data)
    await schedule.save()

    if schedule.enabled:
        await publish_schedule_event(schedule_id, settings=settings, action="add")
    logger.success(f"Расписание {schedule_id} успешно обновлено")
    if data.target_chats:
        # Привязываем чаты к расписанию
        for chat_id in data.target_chats:
            await validate_exists(Chat, chat_id, "Чат")

            await TargetChat.create(schedule=schedule, chat_id=chat_id)

    if data.removed_chats:
        for chat_id in data.removed_chats:
            await validate_exists(Chat, chat_id, "Чат")
            await TargetChat.filter(schedule=schedule, chat_id=chat_id).delete()
    list_scheduled_jobs()
    return ScheduleResponseSchema(schedule_id=schedule.id)


@schedule_router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    _=Depends(require_permission_in_context("delete_schedule")),
    settings=Depends(get_settings),
):
    schedule = await ChatSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    await TargetChat.filter(schedule=schedule).delete()
    await schedule.delete()
    logger.success(f"Расписание {schedule_id} удалено")
    await publish_schedule_event(schedule_id, settings=settings, action="delete")


@schedule_router.get(
    "/all",
    response_model=ScheduleListSchema,
    summary="Получение списка расписаний с фильтрацией",
)
async def get_schedules(
    filters: dict = Depends(schedule_filter_params),
    _=Depends(require_permission_in_context("get_all_schedules")),
):
    logger.info(f"Запрос на список расписаний: {filters}")

    query = Q()

    if filters.get("company_id"):
        query &= Q(company_id=filters["company_id"])

    if filters.get("chat_id"):
        query &= Q(chat_id=filters["chat_id"])

    if filters.get("schedule_type"):
        query &= Q(schedule_type=filters["schedule_type"])

    if filters.get("enabled") is not None:
        query &= Q(enabled=filters["enabled"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
        filters.get('sort_by', 'created_at')
    }"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await ChatSchedule.filter(query).count()

    schedules = (
        await ChatSchedule.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .prefetch_related("chat", "prompt")
        .values(
            "id",
            "prompt_id",
            "schedule_type",
            "enabled",
            "company_id",
            "chat_id",
            "created_at",
            "bot_id",
        )
    )
    return ScheduleListSchema(
        total=total_count,
        schedules=[ScheduleShortSchema(**schedule) for schedule in schedules],
    )


@schedule_router.get("/{schedule_id}", response_model=ScheduleSchema)
async def get_schedule(
    schedule_id: UUID, _=Depends(require_permission_in_context("view_schedule"))
):
    schedule = await ChatSchedule.get_or_none(id=schedule_id).prefetch_related(
        "target_chats", "chat", "prompt", "bot"
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")

    target_chat_ids = (
        await TargetChat.filter(schedule=schedule).prefetch_related("chat").all()
    )
    target_chats = [target_chat.chat.id for target_chat in target_chat_ids]
    return ScheduleSchema(
        schedule_id=schedule.id,
        prompt_id=schedule.prompt.id,
        chat_id=schedule.chat.id,
        schedule_type=schedule.schedule_type,
        interval_hours=schedule.interval_hours,
        interval_minutes=schedule.interval_minutes,
        time_of_day=schedule.time_of_day,
        cron_expression=schedule.cron_expression,
        run_at=schedule.run_at,
        enabled=schedule.enabled,
        time_to_send=schedule.time_to_send,
        send_after_minutes=schedule.send_after_minutes,
        send_strategy=schedule.send_strategy,
        company_id=schedule.company_id,
        created_at=schedule.created_at,
        last_run_at=schedule.last_run_at,
        target_chats=list(target_chats),
        bot_id=schedule.bot.id,
    )

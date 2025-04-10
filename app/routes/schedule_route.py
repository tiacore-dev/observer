from uuid import UUID
from fastapi import APIRouter, Depends,  HTTPException, Body, status
from loguru import logger
from tortoise.expressions import Q
from app.handlers.auth_handlers import get_current_user
from app.database.models import (
    ChatSchedules,
    Users,
    TargetChats,
    Prompts,
    Chats,
    Companies,
    Bots
)
from app.pydantic_models.schedule_schemas import (
    ScheduleCreateSchema,
    ScheduleResponseSchema,
    ScheduleSchema,
    ScheduleEditSchema,
    schedule_filter_params,
    ScheduleListSchema,
    ScheduleShortSchema
)


schedule_router = APIRouter()


@schedule_router.post("/add", response_model=ScheduleResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_schedule(data: ScheduleCreateSchema = Body(...), admin: Users = Depends(get_current_user)):
    # Создаем расписание
    company = await Companies.get_or_none(company_id=data.company)
    chat = await Chats.get_or_none(chat_id=data.chat)
    bot = await Bots.get_or_none(bot_id=data.bot)
    prompt = await Prompts.get_or_none(prompt_id=data.prompt)
    if not company or not chat or not prompt or not bot:
        logger.warning(
            "Компания, чат, бот или промпт не найдены при создании расписания")
        raise HTTPException(
            status_code=404, detail="Компания, чат или промпт не найдены")
    try:
        schedule = await ChatSchedules.create(
            prompt=prompt,
            chat=chat,
            schedule_type=data.schedule_type,
            interval_hours=data.interval_hours,
            interval_minutes=data.interval_minutes,
            time_of_day=data.time_of_day,
            cron_expression=data.cron_expression,
            run_at=data.run_at,
            enabled=data.enabled,
            time_to_send=data.time_to_send,
            company=company,
            bot=bot
        )

        # Привязываем чаты к расписанию
        for chat_id in data.target_chats:
            await TargetChats.create(schedule=schedule, chat_id=chat_id)

        return ScheduleResponseSchema(schedule_id=schedule.schedule_id)

    except Exception as e:
        logger.exception(f"Ошибка при создании расписания: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@schedule_router.patch("/{schedule_id}", response_model=ScheduleResponseSchema)
async def edit_schedule(schedule_id: UUID, data: ScheduleEditSchema = Body(...), admin: Users = Depends(get_current_user)):
    updated_data = data.model_dump(exclude_unset=True)
    schedule = await ChatSchedules.get_or_none(schedule_id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    if "company" in updated_data:
        company = await Companies.get_or_none(company_id=data.company)
        updated_data['company'] = company

    if "chat" in updated_data:
        chat = await Chats.get_or_none(chat_id=data.chat)
        updated_data['chat'] = chat
    if "prompt" in updated_data:
        prompt = await Prompts.get_or_none(prompt_id=data.prompt)
        updated_data['prompt'] = prompt

    if "bot" in updated_data:
        bot = await Bots.get_or_none(bot_id=data.bot)
        updated_data['bot'] = bot

    if "time_of_day" in updated_data:
        updated_data["time_of_day"] = updated_data["time_of_day"].isoformat()

    try:
        updated_rows = await ChatSchedules.filter(schedule_id=schedule_id).update(**updated_data)

        if not updated_rows:
            logger.warning(f"Расписание {schedule_id} не найдено")
            raise HTTPException(
                status_code=404, detail="Расписание не найдено")

        logger.success(f"Расписание {schedule_id} успешно обновлено")
        if data.target_chats:
            # Привязываем чаты к расписанию
            for chat_id in data.target_chats:
                chat = await Chats.get_or_none(chat_id=chat_id)
                await TargetChats.create(schedule=schedule, chat=chat)

        if data.removed_chats:
            for chat_id in data.removed_chats:
                chat = await Chats.get_or_none(chat_id=chat_id)
                await Chats.filter(chat=chat).delete()

        return ScheduleResponseSchema(schedule_id=schedule.schedule_id)

    except Exception as e:
        logger.exception(f"Ошибка при создании расписания: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@schedule_router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(schedule_id: UUID, admin: Users = Depends(get_current_user)):
    schedule = await ChatSchedules.get_or_none(schedule_id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    try:
        await TargetChats.filter(schedule=schedule).delete()
        await schedule.delete()
        logger.success(f"Расписание {schedule_id} удалено")
    except Exception as e:
        logger.exception(f"Ошибка при удалении расписания {schedule_id}")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@schedule_router.get("/all", response_model=ScheduleListSchema, summary="Получение списка расписаний с фильтрацией")
async def get_schedules(
    # 👈 у тебя опечатка в названии, лучше переименовать :)
    filters: dict = Depends(schedule_filter_params),
    user: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на список расписаний: {filters}")
    try:
        query = Q()

        if filters.get("company"):
            query &= Q(company_id=filters["company"])

        if filters.get("chat"):
            query &= Q(chat_id=filters["chat"])

        if filters.get("schedule_type"):
            query &= Q(schedule_type=filters["schedule_type"])

        if filters.get("enabled") is not None:
            query &= Q(enabled=filters["enabled"])

        if filters.get("schedule_type"):
            query &= Q(schedule_type=filters["schedule_type"])

        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{filters.get('sort_by', 'created_at')}"
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        total_count = await ChatSchedules.filter(query).count()

        schedules = await ChatSchedules.filter(query).order_by(order_by).offset(
            (page - 1) * page_size
        ).limit(page_size).prefetch_related("chat", "prompt").values(
            "schedule_id",
            "prompt_id",
            "schedule_type",
            "enabled",
            "company_id",
            "chat_id",
            "created_at",
            "bot"
        )

        return ScheduleListSchema(
            total=total_count,
            schedules=[
                ScheduleShortSchema(
                    schedule_id=s["schedule_id"],
                    prompt=s["prompt_id"],
                    schedule_type=s["schedule_type"],
                    enabled=s["enabled"],
                    company=s["company_id"],
                    chat=s["chat_id"],
                    created_at=s["created_at"]
                )
                for s in schedules
            ]
        )

    except Exception as e:
        logger.exception("Ошибка при получении списка расписаний")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@schedule_router.get("/{schedule_id}", response_model=ScheduleSchema)
async def get_schedule(schedule_id: UUID, admin: Users = Depends(get_current_user)):
    schedule = await ChatSchedules.get_or_none(schedule_id=schedule_id).prefetch_related("target_chats", "company", "chat", "prompt")
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")

    target_chats = await schedule.target_chats.all().values_list("chat_id", flat=True)

    return ScheduleSchema(
        schedule_id=schedule.schedule_id,
        prompt=schedule.prompt.prompt_id,
        chat=schedule.chat.chat_id,
        schedule_type=schedule.schedule_type,
        interval_hours=schedule.interval_hours,
        interval_minutes=schedule.interval_minutes,
        time_of_day=schedule.time_of_day,
        cron_expression=schedule.cron_expression,
        run_at=schedule.run_at,
        enabled=schedule.enabled,
        time_to_send=schedule.time_to_send,
        company=schedule.company.company_id,
        created_at=schedule.created_at,
        last_run_at=schedule.last_run_at,
        target_chats=list(target_chats)
    )

from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends,  HTTPException, Body, status, Path
from loguru import logger
from tortoise.expressions import Q
from app.handlers.auth_handlers import get_current_user
from app.database.models import (
    Users,
    AnalysisResult,
    Companies,
    Prompts,
    Chats,
    Messages
)
from app.pydantic_models.analysis_schema import (
    AnalysisCreateSchema,
    AnalysisResponseSchema,
    AnalysisSchema,
    AnalysisListSchema,
    AnalysisShortSchema,
    analysis_filter_params
)
from app.yandex_funcs.yandex_funcs import yandex_analyze


analysis_router = APIRouter()


@analysis_router.post("/create", response_model=AnalysisResponseSchema, summary="Добавление новой промпта", status_code=status.HTTP_201_CREATED)
async def create_analysis(data: AnalysisCreateSchema = Body(...), admin: Users = Depends(get_current_user)):
    logger.info(f"Создание анализа: {data.dict()}")
    try:
        company = await Companies.get_or_none(company_id=data.company)
        prompt = await Prompts.get_or_none(prompt_id=data.prompt)
        chat = await Chats.get_or_none(chat_id=data.chat)
        if not company or not prompt or not chat:
            raise HTTPException(
                status_code=400, detail="Компания или промпт не найдены")
        date_from_dt = datetime.fromtimestamp(data.date_from)
        date_to_dt = datetime.fromtimestamp(data.date_to)
        messages = await Messages.filter(chat=chat, timestamp__gte=date_from_dt,
                                         timestamp__lte=date_to_dt).order_by("timestamp").prefetch_related("account", "chat").all()
        logger.debug(f"Найдено {len(messages)} сообщений.")
        result_text, tokens_input, tokens_output = await yandex_analyze(prompt, messages)
        analysis = await AnalysisResult.create(
            result_text=result_text,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            prompt=prompt,
            chat=chat,
            date_from=data.date_from,
            date_to=data.date_to,
            company=company
        )
        logger.success(
            f"Анализ успешно создан с id {analysis.analysis_id}")
        return AnalysisResponseSchema(analysis_id=analysis.analysis_id)
    except Exception as e:
        logger.exception("Ошибка при создании анализа")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@analysis_router.get("/all", response_model=AnalysisListSchema, summary="Получение списка анализов с фильтрацией")
async def get_analyses(
    filters: dict = Depends(analysis_filter_params),
    user: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на список анализов: {filters}")
    try:
        query = Q()

        if filters.get("company"):
            query &= Q(company_id=filters["company"])
        if filters.get("chat"):
            query &= Q(chat_id=filters["chat"])
        if filters.get("schedule"):
            query &= Q(schedule_id=filters["schedule"])

        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{filters.get('sort_by', 'created_at')}"
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        total_count = await AnalysisResult.filter(query).count()

        analyses = await AnalysisResult.filter(query).order_by(order_by).offset(
            (page - 1) * page_size
        ).limit(page_size).values(
            "analysis_id",
            "prompt_id",
            "chat_id",
            "company_id",
            "created_at",
            "tokens_input",
            "tokens_output"
        )

        logger.success(f"Найдено анализов: {len(analyses)} из {total_count}")
        return AnalysisListSchema(
            total=total_count,
            analysis=[
                AnalysisShortSchema(
                    analysis_id=a["analysis_id"],
                    prompt=a["prompt_id"],
                    chat=a["chat_id"],
                    company=a["company_id"],
                    created_at=a["created_at"],
                    tokens_input=a["tokens_input"],
                    tokens_output=a["tokens_output"]
                )
                for a in analyses
            ]
        )

    except Exception as e:
        logger.exception("Ошибка при получении списка анализов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@analysis_router.get(
    "/{analysis_id}",
    response_model=AnalysisSchema,
    summary="Просмотр анализа"
)
async def get_analysis(
    analysis_id: UUID = Path(..., title="ID анализа",
                             description="ID просматриваемого анализа"),
    admin: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на просмотр анализа: {analysis_id}")
    try:
        analysis = await AnalysisResult.filter(analysis_id=analysis_id).first().values(
            "analysis_id",
            "prompt_id",
            "chat_id",
            "result_text",
            "schedule_id",
            "company_id",
            "created_at",
            "date_to",
            "date_from",
            "tokens_input",
            "tokens_output",
            "send_time"
        )

        if analysis is None:
            logger.warning(f"Анализ {analysis_id} не найден")
            raise HTTPException(status_code=404, detail="Анализ не найден")

        analysis_schema = AnalysisSchema(
            analysis_id=analysis["analysis_id"],
            prompt=analysis["prompt_id"],
            chat=analysis["chat_id"],
            result_text=analysis["result_text"],
            schedule=analysis["schedule_id"],
            company=analysis["company_id"],
            created_at=analysis["created_at"],
            date_to=analysis["date_to"],
            date_from=analysis["date_from"],
            tokens_input=analysis["tokens_input"],
            tokens_output=analysis["tokens_output"],
            send_time=analysis["send_time"]
        )

        logger.success(f"Анализ найден: {analysis_schema.analysis_id}")
        return analysis_schema

    except Exception as e:
        logger.exception("Ошибка при просмотре анализа")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e

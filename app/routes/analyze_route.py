# from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends,  HTTPException, Body, status
from loguru import logger
# from tortoise.expressions import Q
from app.handlers.auth_handlers import get_current_user
from app.database.models import (
    Users,
    # ChatSchedules,
    AnalysisResult,
    Companies,
    Prompts,
    Chats,
    Messages
)
from app.pydantic_models.analyze_schema import (
    AnalysisCreateSchema,
    AnalysisResponseSchema,

)
from app.yandex_funcs.yandex_funcs import yandex_analyze


analyze_router = APIRouter()


@analyze_router.post("/create", response_model=AnalysisResponseSchema, summary="Добавление новой промпта", status_code=status.HTTP_201_CREATED)
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

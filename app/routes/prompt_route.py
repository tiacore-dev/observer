from uuid import UUID
from fastapi import APIRouter, Depends, Path, HTTPException, Body, status
from loguru import logger
from tortoise.expressions import Q
from app.handlers.auth_handlers import get_current_user
from app.database.models import Prompts, Users, Companies
from app.pydantic_models.prompt_schemas import (
    PromptCreateSchema,
    PromptEditSchema,
    prompt_filter_params,
    PromptResponseSchema,
    PromptListResponseSchema,
    PromptSchema
)


prompt_router = APIRouter()


@prompt_router.post("/add", response_model=PromptResponseSchema, summary="Добавление новой промпта", status_code=status.HTTP_201_CREATED)
async def add_prompt(data: PromptCreateSchema = Body(...), admin: Users = Depends(get_current_user)):
    logger.info(f"Создание промпта: {data.dict()}")
    try:
        company = await Companies.get_or_none(company_id=data.company)
        if not company:
            raise HTTPException(status_code=400, detail="Компания не найдена")
        prompt = await Prompts.create(
            prompt_name=data.prompt_name,
            text=data.text,
            company=company)
        if not prompt:
            logger.error("Не удалось создать промпту")
            raise HTTPException(
                status_code=500, detail="Не удалось создать промпту")

        logger.success(
            f"промпта {prompt.prompt_name} ({prompt.prompt_id}) успешно создана")
        return {"prompt_id": str(prompt.prompt_id)}
    except Exception as e:
        logger.exception("Ошибка при создании промпта")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@prompt_router.patch("/{prompt_id}", summary="Изменение промпта", status_code=status.HTTP_204_NO_CONTENT)
async def edit_prompt(
        prompt_id: UUID = Path(..., title="ID промпта",
                               description="ID изменяемой промпта"),
        data: PromptEditSchema = Body(...),
        admin: Users = Depends(get_current_user)):
    """
    Обновление промпта по ID, переданному в URL.
    """
    logger.info(
        f"Обновление промпта {prompt_id}: {data.dict(exclude_unset=True)}")
    try:
        updated_rows = await Prompts.filter(prompt_id=prompt_id).update(**data.dict(exclude_unset=True))

        if not updated_rows:
            logger.warning(f"промпта {prompt_id} не найдена")
            raise HTTPException(status_code=404, detail="промпта не найдена")

        logger.success(f"промпта {prompt_id} успешно обновлена")

    except Exception as e:
        logger.exception("Ошибка при обновлении промпта")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@prompt_router.delete("/{prompt_id}", summary="Удаление промпта", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
        prompt_id: UUID = Path(..., title="ID промпта",
                               description="ID удаляемой промпта"),
        admin: Users = Depends(get_current_user)):
    logger.info(f"Удаление промпта {prompt_id}")
    try:
        deleted_count = await Prompts.filter(prompt_id=prompt_id).delete()
        if not deleted_count:
            logger.warning(f"промпта {prompt_id} не найдена")
            raise HTTPException(status_code=404, detail="промпта не найдена")

        logger.success(f"промпта {prompt_id} успешно удалена")
        # return {"detail": "промпта успешно удалена"}
    except Exception as e:
        logger.exception("Ошибка при удалении промпта")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@prompt_router.get("/all", response_model=PromptListResponseSchema, summary="Получение списка промптов с фильтрацией")
async def get_prompts(
    filters: dict = Depends(prompt_filter_params),
    user: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на список промптов: {filters}")

    try:
        query = Q()

        if filters.get("company"):
            query &= Q(company=filters["company"])

        if filters.get("search"):
            query &= Q(prompt_name__icontains=filters["search"])

        order_by = f"{'-' if filters.get('order') == 'desc' else ''}{filters.get('sort_by', 'prompt_name')}"
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)

        total_count = await Prompts.filter(query).count()

        prompts = await Prompts.filter(query).order_by(order_by).offset(
            (page - 1) * page_size
        ).limit(page_size).values(
            "prompt_id",
            "prompt_name",
            "text",
            "company_id",
            "created_at"
        )

        return PromptListResponseSchema(
            total=total_count,
            prompts=[
                PromptSchema(
                    prompt_id=p["prompt_id"],
                    prompt_name=p["prompt_name"],
                    text=p["text"],
                    company=p["company_id"],
                    created_at=p["created_at"]
                )
                for p in prompts
            ]
        )

    except Exception as e:
        logger.exception("Ошибка при получении списка промптов")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@prompt_router.get("/{prompt_id}", response_model=PromptSchema, summary="Просмотр промпта")
async def get_prompt(
    prompt_id: UUID = Path(..., title="ID промпта",
                           description="ID просматриваемого промпта"),
    admin: Users = Depends(get_current_user)
):
    logger.info(f"Запрос на просмотр промпта: {prompt_id}")
    try:
        prompt = await Prompts.filter(prompt_id=prompt_id).first().values(
            "prompt_id",
            "prompt_name",
            "text",
            "company_id",
            "created_at"
        )

        if prompt is None:
            logger.warning(f"Промпт {prompt_id} не найден")
            raise HTTPException(status_code=404, detail="Промпт не найден")

        prompt_schema = PromptSchema(
            prompt_id=prompt["prompt_id"],
            prompt_name=prompt["prompt_name"],
            text=prompt["text"],
            company=prompt["company_id"],
            created_at=prompt["created_at"]
        )

        logger.success(f"Промпт найден: {prompt_schema}")
        return prompt_schema
    except Exception as e:
        logger.exception("Ошибка при просмотре промпта")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e

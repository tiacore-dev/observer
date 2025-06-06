from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Prompt
from app.pydantic_models.prompt_schemas import (
    PromptCreateSchema,
    PromptEditSchema,
    PromptListResponseSchema,
    PromptResponseSchema,
    PromptSchema,
    prompt_filter_params,
)

prompt_router = APIRouter()


@prompt_router.post(
    "/add",
    response_model=PromptResponseSchema,
    summary="Добавление новой промпта",
    status_code=status.HTTP_201_CREATED,
)
async def add_prompt(
    data: PromptCreateSchema = Body(...),
    _=Depends(require_permission_in_context("add_prompt")),
):
    prompt = await Prompt.create(**data.model_dump(exclude_unset=True))
    if not prompt:
        logger.error("Не удалось создать промпту")
        raise HTTPException(status_code=500, detail="Не удалось создать промпту")

    logger.success(f"промпта {prompt.name} ({prompt.id}) успешно создана")
    return {"prompt_id": str(prompt.id)}


@prompt_router.patch(
    "/{prompt_id}", summary="Изменение промпта", status_code=status.HTTP_204_NO_CONTENT
)
async def edit_prompt(
    prompt_id: UUID = Path(
        ..., title="ID промпта", description="ID изменяемой промпта"
    ),
    data: PromptEditSchema = Body(...),
    _=Depends(require_permission_in_context("edit_prompt")),
):
    logger.info(f"Обновление промпта {prompt_id}")

    prompt = await Prompt.filter(id=prompt_id).first()
    if not prompt:
        logger.warning(f"промпта {prompt_id} не найдена")
        raise HTTPException(status_code=404, detail="промпта не найдена")
    await prompt.update_from_dict(data.model_dump(exclude_unset=True))
    await prompt.save()


@prompt_router.delete(
    "/{prompt_id}", summary="Удаление промпта", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_prompt(
    prompt_id: UUID = Path(..., title="ID промпта", description="ID удаляемой промпта"),
    _=Depends(require_permission_in_context("delete_prompt")),
):
    prompt = await Prompt.filter(id=prompt_id).first()
    if not prompt:
        logger.warning(f"промпта {prompt_id} не найдена")
        raise HTTPException(status_code=404, detail="промпта не найдена")
    await prompt.delete()


@prompt_router.get(
    "/all",
    response_model=PromptListResponseSchema,
    summary="Получение списка промптов с фильтрацией",
)
async def get_prompts(
    filters: dict = Depends(prompt_filter_params),
    _=Depends(require_permission_in_context("get_all_prompts")),
):
    query = Q()

    if filters.get("company_id"):
        query &= Q(company_id=filters["company_id"])

    if filters.get("prompt_name"):
        query &= Q(name__icontains=filters["prompt_name"])
    if filters.get("text"):
        query &= Q(text__icontains=filters["text"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
        filters.get('sort_by', 'name')
    }"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await Prompt.filter(query).count()

    prompts = (
        await Prompt.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "text", "company_id", "created_at")
    )

    return PromptListResponseSchema(
        total=total_count,
        prompts=[PromptSchema(**prompt) for prompt in prompts],
    )


@prompt_router.get(
    "/{prompt_id}", response_model=PromptSchema, summary="Просмотр промпта"
)
async def get_prompt(
    prompt_id: UUID = Path(
        ..., title="ID промпта", description="ID просматриваемого промпта"
    ),
    _=Depends(require_permission_in_context("view_prompt")),
):
    logger.info(f"Запрос на просмотр промпта: {prompt_id}")
    prompt = (
        await Prompt.filter(id=prompt_id)
        .first()
        .values("id", "name", "text", "company_id", "created_at")
    )

    if prompt is None:
        logger.warning(f"Промпт {prompt_id} не найден")
        raise HTTPException(status_code=404, detail="Промпт не найден")

    prompt_schema = PromptSchema(**prompt)

    logger.success(f"Промпт найден: {prompt_schema}")
    return prompt_schema

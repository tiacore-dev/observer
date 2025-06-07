import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class PromptCreateSchema(CleanableBaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="prompt_name")
    text: str = Field(...)
    company_id: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class PromptEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, alias="prompt_name")
    text: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class PromptSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="prompt_id")
    name: str = Field(..., alias="prompt_name")
    text: str
    created_at: datetime.datetime
    company_id: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class PromptResponseSchema(CleanableBaseModel):
    prompt_id: UUID


class PromptListResponseSchema(CleanableBaseModel):
    total: int
    prompts: List[PromptSchema]


def prompt_filter_params(
    prompt_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    text: Optional[str] = Query(None, description="Фильтр по тексту"),
    company_id: Optional[UUID] = Query(None),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "prompt_name": prompt_name,
        "text": text,
        "company_id": company_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

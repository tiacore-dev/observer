from typing import List, Optional
import datetime
from pydantic import BaseModel, UUID4, Field
from fastapi import Query


class PromptCreateSchema(BaseModel):
    prompt_name: str = Field(..., min_length=3, max_length=100)
    text: str = Field(...)
    company: UUID4 = Field(...)


class PromptEditSchema(BaseModel):
    prompt_name: Optional[str] = Field(None, min_length=3, max_length=100)
    text: Optional[str] = None  # ✅ добавлено = None

    class Config:
        extra = "forbid"


class PromptSchema(BaseModel):
    prompt_id: UUID4
    prompt_name: str
    text: str
    created_at: datetime.datetime
    company: UUID4

    class Config:
        from_attributes = True


class PromptResponseSchema(BaseModel):
    prompt_id: UUID4


class PromptListResponseSchema(BaseModel):
    total: int
    prompts: List[PromptSchema]


def prompt_filter_params(
    search: Optional[str] = Query(
        None, description="Фильтр по названию промпта"),
    company: Optional[UUID4] = Query(None),
    sort_by: Optional[str] = Query(
        "prompt_name", description="Поле сортировки"),
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

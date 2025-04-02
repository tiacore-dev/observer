from typing import List, Optional
from pydantic import BaseModel, UUID4, Field
from fastapi import Query


class PromptCreateSchema(BaseModel):
    prompt_name: str = Field(..., min_length=3, max_length=100)
    text: str = Field(...)


class PromptEditSchema(BaseModel):
    prompt_name: Optional[str] = Field(None, min_length=3, max_length=100)
    text: Optional[str] = None  # ✅ добавлено = None

    class Config:
        extra = "forbid"


class PromptSchema(BaseModel):
    prompt_id: UUID4
    prompt_name: str
    text: str
    use_automatic: Optional[bool] = False
    created_at: int  # Timestamp
    company: UUID4

    class Config:
        from_attributes = True


class PromptResponseSchema(BaseModel):
    prompt_id: UUID4


class PromptListResponseSchema(BaseModel):
    total: int
    prompts: List[PromptSchema]


class PromptAutomaticSchema(BaseModel):
    use_automatic: bool = Field(...)


def prompt_filter_params(
    search: Optional[str] = Query(
        None, description="Фильтр по названию промпта"),
    sort_by: Optional[str] = Query(
        "prompt_name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "search": search,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }

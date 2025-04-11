import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4, Field
from fastapi import Query


class AnalysisCreateSchema(BaseModel):
    prompt: UUID4 = Field(...)
    chat: int = Field(...)
    date_from: int = Field(...)
    date_to: int = Field(...)
    company: UUID4 = Field(...)


class AnalysisResponseSchema(BaseModel):
    analysis_id: UUID4


class AnalysisSchema(BaseModel):
    analysis_id: UUID4
    prompt: UUID4
    chat: int
    result_text: str
    schedule: Optional[UUID4] = None
    company: UUID4
    created_at: datetime.datetime
    date_to: int
    date_from: int
    tokens_input: int
    tokens_output: int
    send_time: Optional[int]


class AnalysisShortSchema(BaseModel):
    analysis_id: UUID4
    prompt: UUID4
    chat: int
    company: UUID4
    created_at: datetime.datetime
    tokens_input: int
    tokens_output: int


class AnalysisListSchema(BaseModel):
    total: int
    analysis: List[AnalysisShortSchema]


def analysis_filter_params(
    company: Optional[UUID4] = Query(None),
    chat: Optional[UUID4] = Query(None),
    schedule: Optional[UUID4] = Query(None),
    sort_by: Optional[str] = Query(
        "created_at", description="Поле сортировки"),
    order: Optional[str] = Query("desc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100)
):
    return {
        "company": company,
        "chat": chat,
        "schedule": schedule,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size
    }

from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class CompanyCreateSchema(CleanableBaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="company_name")
    description: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class CompanyEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=100, alias="company_name"
    )
    description: Optional[str] = Field(None)  # ✅ добавлено = None

    class Config:
        from_attributes = True
        populate_by_name = True


class CompanySchema(CleanableBaseModel):
    id: UUID = Field(..., alias="company_id")
    name: str = Field(..., alias="company_name")
    description: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class CompanyResponseSchema(CleanableBaseModel):
    company_id: UUID


class CompanyListResponseSchema(CleanableBaseModel):
    total: int
    companies: List[CompanySchema]


def company_filter_params(
    company_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("desc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "company_name": company_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

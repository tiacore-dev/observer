from typing import List, Optional
from pydantic import BaseModel, UUID4, Field
from fastapi import Query


class CompanyCreateSchema(BaseModel):
    company_name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(None)


class CompanyEditSchema(BaseModel):
    company_name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None)  # ✅ добавлено = None


class CompanySchema(BaseModel):
    company_id: UUID4
    company_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CompanyResponseSchema(BaseModel):
    company_id: UUID4


class CompanyListResponseSchema(BaseModel):
    total: int
    companies: List[CompanySchema]


def company_filter_params(
    search: Optional[str] = Query(
        None, description="Фильтр по названию промпта"),
    sort_by: Optional[str] = Query(
        "company_name", description="Поле сортировки"),
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

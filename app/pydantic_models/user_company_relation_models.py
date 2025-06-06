from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class UserCompanyRelationCreateSchema(CleanableBaseModel):
    user_id: UUID = Field(..., description="UUID пользователя, связанного с компанией")
    company_id: UUID = Field(..., description="UUID компании")
    role_id: UUID = Field(..., description="UUID роли пользователя в компании")

    class Config:
        from_attributes = True


class UserCompanyRelationSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="user_company_id")
    user_id: UUID
    company_id: UUID
    role_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class UserCompanyRelationListResponseSchema(CleanableBaseModel):
    total: int
    relations: List[UserCompanyRelationSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UserCompanyRelationResponseSchema(CleanableBaseModel):
    user_company_id: UUID

    class Config:
        from_attributes = True


class UserCompanyRelationEditSchema(CleanableBaseModel):
    user_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    role_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class UserCompanyRelationFilterSchema(CleanableBaseModel):
    user_id: Optional[UUID] = Field(None, description="Фильтр по пользователю")
    company_id: Optional[UUID] = Field(None, description="Фильтр по компании")
    role_id: Optional[UUID] = Field(None, description="Фильтр по роли")
    sort_by: str = Field("created_at", description="Поле сортировки")
    order: str = Field("desc", description="Порядок сортировки: asc/desc")
    page: int = Field(1, ge=1, description="Номер страницы")
    page_size: int = Field(10, ge=1, le=100, description="Размер страницы")

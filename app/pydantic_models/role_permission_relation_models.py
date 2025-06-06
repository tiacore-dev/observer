from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class RolePermissionRelationCreateSchema(CleanableBaseModel):
    role_id: UUID = Field(..., description="ID роли")
    permission_id: str = Field(..., description="ID разрешения")
    restriction_id: Optional[str] = Field(None, description="ID запрета")

    class Config:
        from_attributes = True


class RolePermissionRelationEditSchema(CleanableBaseModel):
    role_id: Optional[UUID] = None
    permission_id: Optional[str] = None
    restriction_id: Optional[str] = None


class RolePermissionRelationSchema(CleanableBaseModel):
    role_permission_id: UUID
    role_id: UUID
    permission_id: str
    restriction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RolePermissionRelationResponseSchema(CleanableBaseModel):
    role_permission_id: UUID

    class Config:
        from_attributes = True


class RolePermissionRelationListResponseSchema(CleanableBaseModel):
    total: int
    relations: List[RolePermissionRelationSchema]

    class Config:
        from_attributes = True


def role_permission_filter_params(
    role_id: Optional[UUID] = Query(None, description="Фильтр по роли"),
    permission_id: Optional[str] = Query(None, description="Фильтр по разрешению"),
    restriction_id: Optional[str] = Query(None, description="Фильтр по запрету"),
    sort_by: Optional[str] = Query("created_at", description="Поле сортировки"),
    order: Optional[str] = Query("desc", description="Порядок сортировки: asc/desc"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "role_id": role_id,
        "permission_id": permission_id,
        "restriction_id": restriction_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

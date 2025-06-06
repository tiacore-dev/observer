from typing import List, Optional

from fastapi import Query
from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class PermissionsSchema(CleanableBaseModel):
    id: str = Field(..., alias="permission_id")
    name: str = Field(..., alias="permission_name")
    comment: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class PermissionsListResponseSchema(CleanableBaseModel):
    total: int
    permissions: List[PermissionsSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


def permission_filter_params(
    permission_name: Optional[str] = Query(None, description="Фильтр по названию"),
    comment: Optional[str] = Query(None, description="Комментарий к разрешению"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "permission_name": permission_name,
        "comment": comment,
        "page": page,
        "page_size": page_size,
    }

from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class RoleCreateSchema(CleanableBaseModel):
    name: str = Field(..., alias="role_name")
    application_id: str = Field(...)

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class RoleCreateManySchema(CleanableBaseModel):
    name: str = Field(..., alias="role_name")
    permissions: List[str] = Field(
        ..., description="Список ID разрешений, которые будут назначены этой роли"
    )
    application_id: str

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class RoleSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="role_id")
    name: str = Field(..., alias="role_name")
    system_name: Optional[str] = Field(None, alias="role_system_name")
    application_id: str

    class Config:
        from_attributes = True
        populate_by_name = True


class RoleListResponseSchema(CleanableBaseModel):
    total: int
    roles: List[RoleSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class RoleResponseSchema(CleanableBaseModel):
    role_id: UUID

    class Config:
        from_attributes = True


class RoleEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(None, alias="role_name")

    class Config:
        from_attributes = True


class RoleFilterSchema(CleanableBaseModel):
    role_name: Optional[str] = Field(None, description="Фильтр по роли")
    application_id: Optional[str] = Field(None, description="ID приложения")
    sort_by: str = Field("name", description="Поле сортировки")
    order: str = Field("asc", description="asc или desc")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field

from app.pydantic_models.clean_model import CleanableBaseModel


class UserCreateSchema(CleanableBaseModel):
    email: str = Field(
        ..., min_length=3, max_length=50, description="Уникальное имя пользователя"
    )
    password: str = Field(..., min_length=6, description="Пароль (не менее 6 символов)")
    full_name: str = Field(
        ..., min_length=3, max_length=100, description="Полное имя пользователя"
    )

    company_id: UUID = Field(...)

    class Config:
        from_attributes = True


class UserEditSchema(CleanableBaseModel):
    email: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    is_verified: Optional[bool] = Field(None)


class UserSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="user_id")
    email: str
    full_name: str
    position: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True
        populate_by_name = True


class UserListResponseSchema(CleanableBaseModel):
    total: int
    users: List[UserSchema]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UserResponseSchema(CleanableBaseModel):
    user_id: UUID


def user_filter_params(
    email: Optional[str] = Query(None, description="Фильтр по названию"),
    full_name: Optional[str] = Query(None, description="Фильтр по названию"),
    company_id: Optional[UUID] = Query(None, description="Фильтр по компании"),
    sort_by: Optional[str] = Query("email", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="Порядок сортировки: asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "email": email,
        "full_name": full_name,
        "company_id": company_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }

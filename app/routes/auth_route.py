import aiohttp
from fastapi import APIRouter, Body, Depends
from tiacore_lib.config import get_settings
from tiacore_lib.pydantic_models.auth_models import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)

auth_router = APIRouter()


@auth_router.post(
    "/login", response_model=TokenResponse, summary="Авторизация пользователя"
)
async def login(
    data: LoginRequest,
    settings=Depends(get_settings),
):
    payload = dict(data.model_dump())
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.AUTH_URL}/api/auth/login",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300),
        ) as response:
            response_data = await response.json()
            return TokenResponse(**response_data)


@auth_router.post(
    "/refresh", response_model=TokenResponse, summary="Обновление Access Token"
)
async def refresh_access_token(
    data: RefreshRequest = Body(...),
    settings=Depends(get_settings),
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.AUTH_URL}/api/auth/refresh",
            json=data.model_dump(),
            timeout=aiohttp.ClientTimeout(total=300),
        ) as response:
            response_data = await response.json()
            return TokenResponse(**response_data)

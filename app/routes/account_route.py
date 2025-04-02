from fastapi import APIRouter, Depends
# Depends, который парсит JWT
from app.handlers.auth_handlers import get_current_user
# или только AdminUser, если ты хочешь только для админов
from app.database.models import AdminUser

account_router = APIRouter()


@account_router.get("/info")
async def get_account_info(admin: AdminUser = Depends(get_current_user)):

    return {
        "username": admin.username,
        "company_name": admin.company.company_name,
    }

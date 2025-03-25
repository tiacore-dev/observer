from fastapi import APIRouter, Depends
# Depends, который парсит JWT
from app.handlers.auth_handlers import get_current_user
# или только AdminUser, если ты хочешь только для админов
from app.database.models import AdminUser

account_router = APIRouter(prefix="/api/accounts")


@account_router.get("/info")
async def get_account_info(username: str = Depends(get_current_user)):
    user = await AdminUser.filter(username=username).prefetch_related("company").first()
    return {
        "username": user.username,
        "company_name": user.company.company_name,
    }

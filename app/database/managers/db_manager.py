from fastapi import Query, HTTPException
from tortoise.exceptions import DoesNotExist
from app.database.models import User


async def get_user_by_telegram_id(telegram_id: int = Query(...)) -> User:
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# async def get_user_by_telegram_id(telegram_id: int):
#     """
#     Получить пользователя по Telegram ID.
#     """
#     try:
#         return await User.get(telegram_id=telegram_id)
#     except DoesNotExist:
#         return None


async def get_admin_user(telegram_id: int):
    """
    Получить админа по Telegram ID.
    """
    try:
        return await User.get(telegram_id=telegram_id)
    except DoesNotExist:
        return None

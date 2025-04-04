from fastapi import APIRouter, HTTPException, Depends, status
from app.handlers.telegram_api_url_handlers import validate_token_and_register
from app.handlers.auth_handlers import get_current_user
from app.database.models import Users
from app.pydantic_models.bot_schemas import RegisterBotRequest

bot_router = APIRouter()


@bot_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_bot(data: RegisterBotRequest, user: Users = Depends(get_current_user)):
    try:
        bot = await validate_token_and_register(data.token, data.company)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid bot token") from e
    return {"bot_id": bot.bot_id}

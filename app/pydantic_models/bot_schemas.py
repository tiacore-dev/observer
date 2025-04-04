from pydantic import BaseModel, UUID4


class RegisterBotRequest(BaseModel):
    token: str
    company: UUID4


class BotResponseModel(BaseModel):
    bot_id: int


# class BotModel(BaseModel):

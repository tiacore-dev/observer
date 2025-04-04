from .auth_route import auth_router
from .bot_route import bot_router
from .prompt_route import prompt_router
from .webhook_route import webhook_router


def register_routes(app):
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(
        bot_router, prefix="/api/bots", tags=["Bots"])
    app.include_router(prompt_router, prefix="/api/prompts", tags=["Prompts"])
    app.include_router(
        webhook_router, prefix="/api/webhook", tags=["Webhooks"])

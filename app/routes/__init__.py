from .auth_route import auth_router
from .bot_route import bot_router
from .prompt_route import prompt_router
from .webhook_route import webhook_router
from .schedule_route import schedule_router
from .analyze_route import analyze_router
from .company_route import company_router


def register_routes(app):
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(
        bot_router, prefix="/api/bots", tags=["Bots"])
    app.include_router(prompt_router, prefix="/api/prompts", tags=["Prompts"])
    app.include_router(
        webhook_router, prefix="/api/webhook", tags=["Webhooks"])
    app.include_router(
        schedule_router, prefix="/api/schedules", tags=["Schedules"])
    app.include_router(
        analyze_router, prefix="/api/analysis", tags=["Analysis"])
    app.include_router(
        company_router, prefix="/api/companies", tags=["Companies"])

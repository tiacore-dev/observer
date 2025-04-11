from .auth_route import auth_router
from .bot_route import bot_router
from .prompt_route import prompt_router
from .webhook_route import webhook_router
from .schedule_route import schedule_router
from .analysis_route import analysis_router
from .company_route import company_router
from .monitoring_route import monitoring_router
from .get_route import get_router


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
        analysis_router, prefix="/api/analysis", tags=["Analysis"])
    app.include_router(
        company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(monitoring_router, tags=["Monitoring"])
    app.include_router(get_router, prefix="/api", tags=["Get"])

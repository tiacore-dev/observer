from .auth_route import auth_router
from .frontend_route import frontend_router
from .account_route import account_router
from .prompt_route import prompt_router


def register_routes(app):
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(frontend_router, tags=["Frontend"])
    app.include_router(
        account_router, prefix="/api/accounts", tags=["Accounts"])
    app.include_router(prompt_router, prefix="/api/prompts", tags=["Prompts"])

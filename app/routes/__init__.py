from .auth_route import auth_router
from .frontend_route import frontend_router


def register_routes(app):
    app.include_router(auth_router)
    app.include_router(frontend_router)

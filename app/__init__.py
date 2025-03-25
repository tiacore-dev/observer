import os
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from logger import setup_logger
from app.routes import register_routes
from config import Settings


def create_app() -> FastAPI:
    app = FastAPI(title="Observer", redirect_slashes=False)
    settings = Settings()
    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=settings.ALLOWED_HOSTS)

    app.add_middleware(GZipMiddleware)
    # app.add_middleware(HTTPSRedirectMiddleware)

   # Конфигурация Tortoise ORM
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.database.models"]},
        # generate_schemas=True,
        add_exception_handlers=True,
    )

    setup_logger()
    # Регистрация маршрутов
    register_routes(app)

    # Раздача статических файлов
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app

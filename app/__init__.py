from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from logger import setup_logger
from app.routes import register_routes

from config import Settings


def create_app() -> FastAPI:
    app = FastAPI(title="Observer", redirect_slashes=False)
    settings = Settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  # Разрешаем использование кук и авторизации
        allow_methods=["*"],
        allow_headers=["*"],  # Разрешаем все заголовки
    )

    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.database.models"]},
        # generate_schemas=True,
        add_exception_handlers=True,
    )

    setup_logger()

    register_routes(app)

    return app

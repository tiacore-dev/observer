from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from prometheus_client import make_asgi_app
from metrics.logger import setup_logger
from metrics.tracer import init_tracer
from app.routes import register_routes
from config import Settings


def create_app(config_name='Development') -> FastAPI:
    app = FastAPI(title="Observer", redirect_slashes=False)
    settings = Settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  # Разрешаем использование кук и авторизации
        allow_methods=["*"],
        allow_headers=["*"],  # Разрешаем все заголовки
    )

    if config_name == 'Test':
        db_url = settings.TEST_DATABASE_URL
    else:
        app.mount("/metrics", make_asgi_app())
        init_tracer(app)
        db_url = settings.DATABASE_URL

    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": ["app.database.models"]},
        generate_schemas=(config_name == 'Test'),
        add_exception_handlers=True,
    )

    setup_logger()

    register_routes(app)

    return app

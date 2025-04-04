from fastapi import FastAPI  # , Request
from fastapi.middleware.gzip import GZipMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from tortoise.contrib.fastapi import register_tortoise
from logger import setup_logger
from app.routes import register_routes
# from app.exceptions.catch_middleware import CatchAllExceptionsMiddleware
from config import Settings


def create_app() -> FastAPI:
    app = FastAPI(title="Observer", redirect_slashes=False)
    settings = Settings()
    # app.add_middleware(TrustedHostMiddleware,
    #                   allowed_hosts=settings.ALLOWED_HOSTS)

    app.add_middleware(GZipMiddleware)
    # app.add_middleware(CatchAllExceptionsMiddleware)
    # app.add_middleware(HTTPSRedirectMiddleware)

   # Конфигурация Tortoise ORM
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.database.models"]},
        # generate_schemas=True,
        add_exception_handlers=True,
    )

    # @app.middleware("http")
    # async def log_raw_requests(request: Request, call_next):
    #     body = await request.body()
    #     print(
    #         f"\n>>> RAW REQUEST <<<\nURL: {request.url}\nHeaders: {dict(request.headers)}\nBody: {body.decode('utf-8', errors='ignore')}")
    #     response = await call_next(request)
    #     return response

    setup_logger()
    # Регистрация маршрутов
    register_routes(app)

    return app

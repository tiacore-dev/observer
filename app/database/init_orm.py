from tortoise import Tortoise
from loguru import logger
from config import Settings

settings = Settings()


async def init_db():
    logger.info("🔌 Инициализация Tortoise ORM без FastAPI")
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.database.models"]}
    )
    await Tortoise.generate_schemas()
    logger.info("✅ База данных готова")

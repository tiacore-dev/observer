import asyncio
from loguru import logger
from app.scheduler.scheduler import start_scheduler
from app.scheduler.rabbit_consumer import consume_schedule_events
from app.database.init_orm import init_db
from metrics.logger import setup_logger

setup_logger()


async def main():
    await init_db()

    # запускаем обе корутины как фоновые задачи
    asyncio.create_task(consume_schedule_events())
    asyncio.create_task(start_scheduler())

    logger.info("✅ Consumer и планировщик запущены")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

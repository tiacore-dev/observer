import asyncio
from app.scheduler.scheduler import start_scheduler
from app.scheduler.rabbit_consumer import consume_schedule_events
from app.database.init_orm import init_db
from metrics.logger import setup_logger

setup_logger()


async def keep_alive():
    while True:
        await asyncio.sleep(3600)


async def main():
    await init_db()

    await asyncio.gather(
        consume_schedule_events(),
        start_scheduler(),
        keep_alive()
    )


if __name__ == "__main__":
    asyncio.run(main())

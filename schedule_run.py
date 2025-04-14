import asyncio
from app.scheduler.scheduler import start_scheduler
from app.database.init_orm import init_db
from metrics.logger import setup_logger

setup_logger()


async def main():
    await init_db()
    await start_scheduler()
    while True:
        await asyncio.sleep(3600)  # держим процесс живым

if __name__ == "__main__":
    asyncio.run(main())

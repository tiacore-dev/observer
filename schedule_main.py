import time
import asyncio
from loguru import logger
from logger import setup_logger
from scheduler.scheduler import start_scheduler, scheduler


async def main():
    setup_logger()
    await start_scheduler()
    try:
        while True:
            time.sleep(1)  # Оставляем приложение запущенным
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Планировщик остановлен.")

if __name__ == "__main__":
    asyncio.run(main())

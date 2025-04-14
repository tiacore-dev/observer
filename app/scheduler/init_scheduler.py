from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Инициализация планировщика с использованием SQLAlchemy для хранения задач
scheduler = AsyncIOScheduler(timezone=utc)

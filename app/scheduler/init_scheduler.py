from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

# Инициализация планировщика с использованием SQLAlchemy для хранения задач
scheduler = AsyncIOScheduler(timezone=utc)

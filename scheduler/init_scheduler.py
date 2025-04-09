from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Инициализация планировщика с использованием SQLAlchemy для хранения задач
scheduler = AsyncIOScheduler(timezone='Asia/Novosibirsk')

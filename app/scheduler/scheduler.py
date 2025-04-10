from loguru import logger
from pytz import timezone
from app.scheduler.init_scheduler import scheduler
from app.scheduler.add_or_remove_schedules import add_schedule_job

from app.database.models import ChatSchedules
# Настройка таймзоны Новосибирска
novosibirsk_tz = timezone('Asia/Novosibirsk')


async def start_scheduler():

    schedules = await ChatSchedules.filter(enabled=True).prefetch_related('chat', 'prompt', 'company', 'bot')

    for schedule in schedules:
        add_schedule_job(schedule)

    scheduler.start()
    logger.info("Планировщик успешно запущен с задачами из базы.")


def list_scheduled_jobs():
    """
    Выводит список всех запланированных задач.
    """
    for job in scheduler.get_jobs():
        logger.info(f"Job ID: {job.id}, trigger: {job.trigger}")


def clear_existing_jobs():
    """
    Удаляет все существующие задачи из планировщика.
    """
    try:
        scheduler.remove_all_jobs()
        logger.info("Все задачи успешно удалены из планировщика.")
    except Exception as e:
        logger.error(f"Ошибка при удалении всех задач: {e}")

from loguru import logger
from app.database.models import ChatSchedules
from app.scheduler.init_scheduler import scheduler
from app.scheduler.executors import execute_analysis


def add_schedule_job(sched: ChatSchedules):
    job_id = f"{sched.schedule_id}"

    if sched.schedule_type == "daily_time":
        scheduler.add_job(
            execute_analysis,
            trigger="cron",
            hour=sched.time_of_day.hour,
            minute=sched.time_of_day.minute,
            args=[sched, sched.time_of_day],
            id=job_id,
            replace_existing=True
        )

    elif sched.schedule_type == "interval":
        scheduler.add_job(
            execute_analysis,
            trigger="interval",
            hours=sched.interval_hours or 0,
            minutes=sched.interval_minutes or 0,
            args=[sched, None],
            id=job_id,
            replace_existing=True
        )

    elif sched.schedule_type == "cron":
        from apscheduler.triggers.cron import CronTrigger
        trigger = CronTrigger.from_crontab(sched.cron_expression)
        scheduler.add_job(
            execute_analysis,
            trigger=trigger,
            args=[sched, None],
            id=job_id,
            replace_existing=True
        )

    elif sched.schedule_type == "once":
        scheduler.add_job(
            execute_analysis,
            trigger="date",
            run_date=sched.run_at,
            args=[sched, sched.run_at],
            id=job_id,
            replace_existing=True
        )

    logger.info(f"Задача добавлена: {job_id} ({sched.schedule_type})")


def remove_schedule_job(schedule_id: str):
    try:
        scheduler.remove_job(schedule_id)
        logger.info(f"Задача {schedule_id} успешно удалена из планировщика.")
    except Exception as e:
        logger.warning(f"Не удалось удалить задачу {schedule_id}: {e}")

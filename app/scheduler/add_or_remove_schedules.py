from loguru import logger
from app.database.models import ChatSchedules
from app.scheduler.init_scheduler import scheduler
from app.scheduler.executors import execute_analysis


def add_schedule_job(sched: ChatSchedules):
    job_id = f"{sched.schedule_id}"

    logger.debug(
        f"""Создаём задачу:
        ├─ ID: {job_id}
        ├─ Тип: {sched.schedule_type}
        ├─ Активно: {sched.enabled}
        ├─ Период: hours={sched.interval_hours}, minutes={sched.interval_minutes}
        ├─ Time of day: {sched.time_of_day}
        ├─ Cron: {sched.cron_expression}
        └─ Once: {sched.run_at}"""
    )

    if sched.schedule_type == "daily_time":
        scheduler.add_job(
            execute_analysis,
            trigger="cron",
            hour=sched.time_of_day.hour,
            minute=sched.time_of_day.minute,
            args=[sched],
            id=job_id,
            replace_existing=True
        )

    elif sched.schedule_type == "interval":
        scheduler.add_job(
            execute_analysis,
            trigger="interval",
            hours=sched.interval_hours or 0,
            minutes=sched.interval_minutes or 0,
            args=[sched],
            id=job_id,
            replace_existing=True
        )

    elif sched.schedule_type == "cron":
        from apscheduler.triggers.cron import CronTrigger
        trigger = CronTrigger.from_crontab(sched.cron_expression)
        scheduler.add_job(
            execute_analysis,
            trigger=trigger,
            args=[sched],
            id=job_id,
            replace_existing=True
        )

    elif sched.schedule_type == "once":
        scheduler.add_job(
            execute_analysis,
            trigger="date",
            run_date=sched.run_at,
            args=[sched],
            id=job_id,
            replace_existing=True
        )

    logger.success(
        f"🗓️ Задача {job_id} ({sched.schedule_type}) добавлена в планировщик.")


def remove_schedule_job(schedule_id: str):
    try:
        scheduler.remove_job(schedule_id)
        logger.info(f"🗑️ Задача {schedule_id} удалена из планировщика.")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить задачу {schedule_id}: {e}")

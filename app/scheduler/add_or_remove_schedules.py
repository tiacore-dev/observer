from loguru import logger

from app.database.models import ChatSchedule
from app.scheduler.executors import execute_analysis
from app.scheduler.init_scheduler import scheduler


def add_schedule_job(sched: ChatSchedule, settings):
    job_id = f"{sched.id}"

    logger.debug(
        f"""Создаём задачу:
        ├─ ID: {job_id}
        ├─ Тип: {sched.schedule_type}
       """
    )

    if not sched.enabled:
        logger.info(f"⛔ Задача {job_id} не активна и не будет добавлена.")
        return

    if sched.schedule_type == "interval":
        hours = sched.interval_hours or 0
        minutes = sched.interval_minutes or 0
        if hours == 0 and minutes == 0:
            logger.warning(f"⚠️ Задача {job_id} не добавлена: интервал не задан.")
            return

        scheduler.add_job(
            execute_analysis,
            trigger="interval",
            hours=hours,
            minutes=minutes,
            args=[sched, settings],
            id=job_id,
            replace_existing=True,
        )

    elif sched.schedule_type == "cron":
        if not sched.cron_expression:
            logger.warning(f"⚠️ Задача {job_id} не добавлена: cron-выражение пустое.")
            return
        try:
            from apscheduler.triggers.cron import CronTrigger

            trigger = CronTrigger.from_crontab(sched.cron_expression)
        except Exception as e:
            logger.warning(f"⚠️ Задача {job_id} не добавлена: ошибка в cron-выражении: {e}")
            return

        scheduler.add_job(
            execute_analysis,
            trigger=trigger,
            args=[sched, settings],
            id=job_id,
            replace_existing=True,
        )

    else:
        logger.warning(f"❓ Неизвестный тип задачи: {sched.schedule_type}")
        return

    logger.success(f"🗓️ Задача {job_id} ({sched.schedule_type}) добавлена в планировщик.")


def remove_schedule_job(schedule_id):
    try:
        job = scheduler.get_job(str(schedule_id))
        if job:
            scheduler.remove_job(str(schedule_id))
            logger.info(f"🗑️ Задача {schedule_id} удалена из планировщика.")
        else:
            logger.warning(f"⚠️ Задача {schedule_id} не найдена — возможно, уже выполнена.")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить задачу {schedule_id}: {e}")

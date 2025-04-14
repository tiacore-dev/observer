from datetime import datetime, timedelta, timezone
from loguru import logger
from app.scheduler.tasks import analyze, save_analysis_result, send_analysis_result
from app.scheduler.init_scheduler import scheduler
from app.database.models import Chats, AnalysisResult, TargetChats, ChatSchedules, Bots
from metrics.analysis_metrics import AnalysisMetrics

metrics = AnalysisMetrics()


async def execute_analysis(schedule: ChatSchedules):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат.
    """
    try:
        logger.info(
            f"Выполнение анализа для чата {schedule.chat.chat_id}.")
        data = await analyze(schedule)
        analysis_id = await save_analysis_result(data)

        if analysis_id:
            now = datetime.now(timezone.utc)

            if schedule.send_strategy == "fixed":
                if schedule.time_to_send is None:
                    logger.warning(
                        "time_to_send не указано при стратегии 'fixed'")
                    await send_tasks(schedule, analysis_id)
                    return

                send_time_today = now.replace(
                    hour=schedule.time_to_send.hour,
                    minute=schedule.time_to_send.minute,
                    second=0,
                    microsecond=0
                )

                if now >= send_time_today:
                    logger.info(
                        "Время отправки уже наступило, отправляем результат сразу.")
                    await send_tasks(schedule, analysis_id)
                else:
                    schedule_sending(schedule, analysis_id, send_time_today)

            elif schedule.send_strategy == "relative":
                if schedule.send_after_minutes is None:
                    logger.warning(
                        "send_after_minutes не указано при стратегии 'relative'")
                    # fallback: отправляем сразу
                    await send_tasks(schedule, analysis_id)
                else:
                    send_time = now + \
                        timedelta(minutes=schedule.send_after_minutes)
                    logger.info(
                        f"Планируем отправку через {schedule.send_after_minutes} минут — в {send_time}")
                    schedule_sending(schedule, analysis_id, send_time)

            else:
                logger.warning(
                    f"Неизвестная стратегия отправки: {schedule.send_strategy}. Отправляем сразу.")
                await send_tasks(schedule, analysis_id)
        schedule.last_run_at = datetime.now(timezone.utc)
        await schedule.save()
        logger.info(f"Анализ завершён для чата {schedule.chat.chat_id}.")

        metrics.inc_success(
            chat_id=str(schedule.chat.chat_id),
            schedule_id=str(schedule.schedule_id)
        )

        if schedule.schedule_type == 'once':
            await schedule.delete()

    except Exception as e:
        logger.error(
            f"Ошибка при выполнении анализа для чата {schedule.chat.chat_id}: {e}")
        metrics.inc_failure(
            chat_id=str(schedule.chat.chat_id),
            schedule_id=str(schedule.schedule_id)
        )


def schedule_sending(schedule: ChatSchedules, analysis_id: str, run_at: datetime):
    scheduler.add_job(
        send_tasks,
        trigger="date",
        run_date=run_at,
        args=[schedule, analysis_id],
        id=f"{schedule.schedule_id}_{analysis_id}",
        replace_existing=True
    )


async def send_tasks(schedule: ChatSchedules, analysis_id: str):
    """
    Проверяет задачи, запланированные на текущий час, и выполняет их.
    """

    logger.info(f"Отправка анализа по расписания: {schedule.schedule_id}.")
    try:
        # Получение всех чатов с активным расписанием
        chat = await Chats.get_or_none(chat_id=schedule.chat.chat_id)
        if chat is None:
            logger.error(
                f"Чат не найден для расписания {schedule.schedule_id}")
            return

        try:
            logger.info(f"Обработка чата: {chat.chat_id}.")
            # Получаем результат анализа за последние 24 часа
            analysis = await AnalysisResult.get_or_none(analysis_id=analysis_id)
            target_chats = await TargetChats.filter(schedule=schedule).all()
            bot = await Bots.get_or_none(bot_id=schedule.bot.bot_id)
            if analysis:
                logger.info(f"""Результат анализа найден для чата {
                    chat.chat_id}.""")
                await send_analysis_result(
                    target_chats, chat.chat_name, bot.bot_token, analysis.result_text)
            else:
                logger.warning(f"""Результат анализа для чата {
                    chat.chat_id} за последние 24 часа не найден.""")
                await send_analysis_result(
                    target_chats, chat.chat_name, bot.bot_token, "Результат анализа не найден.")
            logger.info(f"Задача выполнена для чата {chat.chat_id}.")
        except Exception as e:
            logger.error(f"""Ошибка при выполнении задачи для чата {chat.chat_id}: {
                e}""", exc_info=True)

    except Exception as e:
        logger.error(f"Ошибка при проверке задач: {e}", exc_info=True)

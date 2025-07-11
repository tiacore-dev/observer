from datetime import datetime, timedelta, timezone
from uuid import UUID

from loguru import logger

from app.database.models import AnalysisResult, Bot, Chat, ChatSchedule, TargetChat
from app.scheduler.init_scheduler import scheduler
from app.scheduler.tasks import analyze, save_analysis_result, send_analysis_result
from metrics.analysis_metrics import AnalysisMetrics

metrics = AnalysisMetrics()


async def execute_analysis(schedule: ChatSchedule, settings):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат.
    """
    try:
        logger.info(f"Выполнение анализа для чата {schedule.chat.id}.")
        data = await analyze(schedule, settings)
        analysis_id = await save_analysis_result(data)

        if analysis_id:
            now = datetime.now(timezone.utc)

            if schedule.send_strategy == "fixed":
                if schedule.time_to_send is None:
                    logger.warning("time_to_send не указано при стратегии 'fixed'")
                    await send_tasks(schedule, analysis_id)
                    return

                send_time_today = now.replace(
                    hour=schedule.time_to_send.hour,
                    minute=schedule.time_to_send.minute,
                    second=0,
                    microsecond=0,
                )

                if now >= send_time_today:
                    logger.info("Время отправки уже наступило, отправляем результат сразу.")
                    await send_tasks(schedule, analysis_id)
                else:
                    schedule_sending(schedule, analysis_id, send_time_today)

            elif schedule.send_strategy == "relative":
                if schedule.send_after_minutes is None:
                    logger.warning("send_after_minutes не указано при стратегии 'relative'")
                    # fallback: отправляем сразу
                    await send_tasks(schedule, analysis_id)
                else:
                    send_time = now + timedelta(minutes=schedule.send_after_minutes)
                    logger.info(
                        f"""Планируем отправку через {schedule.send_after_minutes} 
                        минут — в {send_time}"""
                    )
                    schedule_sending(schedule, analysis_id, send_time)

            else:
                logger.warning(
                    f"""Неизвестная стратегия отправки: 
                    {schedule.send_strategy}. Отправляем сразу."""
                )
                await send_tasks(schedule, analysis_id)
        schedule.last_run_at = datetime.now(timezone.utc)
        await schedule.save()
        logger.info(f"Анализ завершён для чата {schedule.chat.id}.")

        metrics.inc_success(chat_id=str(schedule.chat.id), schedule_id=str(schedule.id))

        if schedule.schedule_type == "once":
            schedule.enabled = False
            await schedule.save()
            logger.info(f"🧹 Расписание {schedule.id} деактивировано.")

    except Exception as e:
        logger.error(f"Ошибка при выполнении анализа для чата {schedule.chat.id}: {e}")
        metrics.inc_failure(chat_id=str(schedule.chat.id), schedule_id=str(schedule.id))


def schedule_sending(schedule: ChatSchedule, analysis_id: UUID, run_at: datetime):
    scheduler.add_job(
        send_tasks,
        trigger="date",
        run_date=run_at,
        args=[schedule, analysis_id],
        id=f"{schedule.id}_{analysis_id}",
        replace_existing=True,
    )


async def send_tasks(schedule: ChatSchedule, analysis_id):
    """
    Проверяет задачи, запланированные на текущий час, и выполняет их.
    """

    logger.info(f"Отправка анализа по расписания: {schedule.id}.")
    logger.debug(f"📨 Получили analysis_id: {analysis_id} — тип: {type(analysis_id)}")

    try:
        # Получение всех чатов с активным расписанием
        chat = await Chat.get_or_none(id=schedule.chat.id)
        if chat is None:
            logger.error(f"Чат не найден для расписания {schedule.id}")
            return

        try:
            logger.info(f"Обработка чата: {chat.id}.")
            # Получаем результат анализа за последние 2ы4 часа
            analysis = await AnalysisResult.get_or_none(id=analysis_id)
            target_chat_relations = await TargetChat.filter(schedule=schedule).prefetch_related("chat").all()
            target_chats = [target_chat_relation.chat for target_chat_relation in target_chat_relations]
            bot = await Bot.get_or_none(id=schedule.bot.id)
            if not bot:
                raise ValueError()
            if analysis:
                logger.info(f"""Результат анализа найден для чата {chat.id}.""")
                await send_analysis_result(
                    target_chats, chat.name, bot.bot_token, analysis.result_text, schedule.message_intro
                )
            else:
                logger.warning(f"""Результат анализа для чата {chat.id} за последние 24 часа не найден.""")
                await send_analysis_result(
                    target_chats, chat.name, bot.bot_token, "Результат анализа не найден.", schedule.message_intro
                )
            logger.info(f"Задача выполнена для чата {chat.id}.")
        except Exception as e:
            logger.error(
                f"""Ошибка при выполнении задачи для чата {chat.id}: {e}""",
                exc_info=True,
            )

    except Exception as e:
        logger.error(f"Ошибка при проверке задач: {e}", exc_info=True)

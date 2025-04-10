# from datetime import datetime
from pytz import timezone
from loguru import logger
from app.scheduler.tasks import analyze, save_analysis_result, send_analysis_result
from app.scheduler.init_scheduler import scheduler
from app.database.models import Chats, AnalysisResult, TargetChats, ChatSchedules, Bots
from metrics.analysis_metrics import AnalysisMetrics

novosibirsk_tz = timezone('Asia/Novosibirsk')
metrics = AnalysisMetrics()


async def execute_analysis(schedule: ChatSchedules, analysis_time):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат.
    """
    try:
        # Вызов функции анализа (замените на вашу логику)
        logger.info(f"""Выполнение анализа для чата {
            schedule.chat.chat_id} в {analysis_time}.""")
        data = await analyze(schedule, analysis_time)
        analysis_id = await save_analysis_result(data)
        if analysis_id:
            schedule_sending(schedule, analysis_id)
        logger.info(
            f"Анализ завершён для чата {schedule.chat.chat_id}.")
        metrics.inc_success(
            chat_id=str(schedule.chat.chat_id),
            schedule_id=str(schedule.schedule_id)
        )
    except Exception as e:
        logger.error(
            f"Ошибка при выполнении анализа для чата {schedule.chat.chat_id}: {e}")
        metrics.inc_failure(
            chat_id=str(schedule.chat.chat_id),
            schedule_id=str(schedule.schedule_id)
        )


def schedule_sending(schedule: ChatSchedules, analysis_id: str):
    scheduler.add_job(
        send_tasks,
        trigger="date",
        run_date=schedule.time_to_send,
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
                send_analysis_result(
                    target_chats, chat.chat_name, bot.bot_token, analysis.result_text)
            else:
                logger.warning(f"""Результат анализа для чата {
                    chat.chat_id} за последние 24 часа не найден.""")
                send_analysis_result(
                    target_chats, chat.chat_name, bot.bot_token, "Результат анализа не найден.")
            logger.info(f"Задача выполнена для чата {chat.chat_id}.")
        except Exception as e:
            logger.error(f"""Ошибка при выполнении задачи для чата {chat.chat_id}: {
                e}""", exc_info=True)

    except Exception as e:
        logger.error(f"Ошибка при проверке задач: {e}", exc_info=True)


from loguru import logger
from scheduler.tasks import analyze, save_analysis_result, send_analysis_result
from app.database.models import Chats, AnalysisResult


async def execute_analysis(schedule, analysis_time):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат.
    """
    try:
        # Вызов функции анализа (замените на вашу логику)
        logger.info(f"""Выполнение анализа для чата {
            schedule.chat.chat_id} в {analysis_time}.""")
        data = await analyze(schedule, analysis_time)
        await save_analysis_result(data)
        logger.info(
            f"Анализ завершён для чата {schedule.chat.chat_id}.")
    except Exception as e:
        logger.error(
            f"Ошибка при выполнении анализа для чата {schedule.chat.chat_id}: {e}")


async def check_and_execute_tasks():
    """
    Проверяет задачи, запланированные на текущий час, и выполняет их.
    """
    from database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    now = datetime.now(novosibirsk_tz)
    current_hour = now.hour

    logger.info(f"Проверка задач для выполнения в {now.strftime('%H:%M')}.")

    try:
        schedules =
        # Получение всех чатов с активным расписанием
        chats = chat_manager.get_all_chats()
        tasks_to_execute = [
            chat for chat in chats
            if chat.schedule_analysis and chat.analysis_time.hour == current_hour
        ]

        if tasks_to_execute:
            logger.info(
                f"Найдено {len(tasks_to_execute)} задач для выполнения.")
            for chat in tasks_to_execute:
                await execute_analysis(chat.chat_id, chat.analysis_time)
        else:
            logger.info("Нет задач для выполнения в текущий час.")

    except Exception as e:
        logger.error(f"Ошибка при проверке задач: {e}")


def send_tasks():
    """
    Проверяет задачи, запланированные на текущий час, и выполняет их.
    """
    from database.managers.chat_manager import ChatManager
    from database.managers.analysis_manager import AnalysisManager

    chat_manager = ChatManager()
    analysis_manager = AnalysisManager()

    now = datetime.now(novosibirsk_tz)
    current_hour = now.hour

    logger.info(f"Проверка задач для выполнения в {now.strftime('%H:%M')}.")

    try:
        # Получение всех чатов с активным расписанием
        chats = chat_manager.get_all_chats()
        if chats is None:
            logger.error(
                "chat_manager.get_all_chats() вернул None. Ожидается список чатов.")
            return
        logger.info(f"Найдено {len(chats)} чатов для проверки.")

        # Фильтрация чатов по текущему часу
        tasks_to_execute = [
            chat for chat in chats
            if chat.schedule_analysis and chat.send_time.hour == current_hour
        ]
        logger.info(f"""Чатов с задачами на текущий час: {
            len(tasks_to_execute)}.""")

        if tasks_to_execute:
            for chat in tasks_to_execute:
                try:
                    logger.info(f"Обработка чата: {chat.chat_id}.")
                    # Получаем результат анализа за последние 24 часа
                    analysis_result = analysis_manager.get_today_analysis(
                        chat.chat_id)
                    if analysis_result:
                        logger.info(f"""Результат анализа найден для чата {
                            chat.chat_id}.""")
                        send_analysis_result(
                            chat.chat_id, analysis_result.result_text)
                    else:
                        logger.warning(f"""Результат анализа для чата {
                            chat.chat_id} за последние 24 часа не найден.""")
                        send_analysis_result(
                            chat.chat_id, "Результат анализа не найден.")
                    logger.info(f"Задача выполнена для чата {chat.chat_id}.")
                except Exception as e:
                    logger.error(f"""Ошибка при выполнении задачи для чата {chat.chat_id}: {
                        e}""", exc_info=True)
        else:
            logger.info("Нет задач для выполнения в текущий час.")

    except Exception as e:
        logger.error(f"Ошибка при проверке задач: {e}", exc_info=True)

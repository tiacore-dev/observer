# from celery import app

import logging
from datetime import datetime, timedelta

from pytz import timezone, UTC

from app.yandex_funcs.yandex_funcs import yandex_analyze
from app.database.models import (
    Chats,
    AnalysisResult,
    Messages,
    ChatSchedules,
    Prompts
)


novosibirsk_tz = timezone('Asia/Novosibirsk')


async def analyze(schedule: ChatSchedules, analysis_time: datetime):
    """
    Анализирует сообщения в чате за указанный временной промежуток.
    """
    chat_id = schedule.chat.chat_id
    logging.info(f"Начало анализа для чата {chat_id}")

    chat = await Chats.get_or_none(chat_id=chat_id)
    if not chat:
        logging.error(f"Чат {chat_id} не найден.")
        raise ValueError(f"Чат {chat_id} не найден.")

    now_nsk = datetime.now(novosibirsk_tz)

    # now_nsk уже timezone-aware, значит можно безопасно заменять время и отнимать дни
    analysis_start_nsk = now_nsk.replace(
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        microsecond=0
    ) - timedelta(days=1)

    analysis_end_nsk = now_nsk.replace(
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        microsecond=0
    )

    # оба уже имеют tzinfo, можно переводить в UTC
    analysis_start = analysis_start_nsk.astimezone(UTC)
    analysis_end = analysis_end_nsk.astimezone(UTC)

    logging.info(f"Диапазон анализа: {analysis_start} - {analysis_end}")

    try:
        messages = await Messages.filter(chat=chat, timestamp__gte=analysis_start,
                                         timestamp__lte=analysis_end).order_by("timestamp").prefetch_related("account", "chat").all()
    except Exception as e:
        logging.error(f"Ошибка при получении сообщений: {e}")
        raise

    if not messages:
        logging.warning(f"""Нет сообщений для анализа в чате {
                        chat_id} за период {analysis_start} - {analysis_end}.""")
        return {
            "chat": chat,
            "analysis_result": None,
            "tokens_input": 0,
            "tokens_output": 0,
            "prompt": schedule.prompt,
            "schedule": schedule
        }

    logging.info(f"Сообщений для анализа найдено: {len(messages)}")

    try:

        prompt = await Prompts.get_or_none(prompt_id=schedule.prompt.prompt_id)
        if not prompt:
            raise ValueError(
                f"Промпт с ID {chat['default_prompt_id']} не найден.")

        analysis_result, tokens_input, tokens_output = yandex_analyze(
            prompt, messages)
    except Exception as e:
        logging.error(f"Ошибка при анализе сообщений: {e}")
        raise

    logging.info(f"Анализ завершён для чата {chat_id}.")
    return {
        "chat": chat,
        "analysis_result": analysis_result,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "prompt": prompt,
        "schedule": schedule
    }


async def save_analysis_result(data):
    """
    Сохраняет результат анализа в базу данных.
    """
    logging.info(f"Сохранение результата анализа для чата {data['chat_id']}.")

    if data["analysis_result"]:
        await AnalysisResult.create(
            prompt=data["prompt"],
            chat=data['chat'],
            result_text=data["analysis_result"],
            tokens_input=data["tokens_input"],
            tokens_outpu=data["tokens_output"],
            schedule=data['schedule']
        )
        logging.info(f"Результат анализа сохранён для чата {data['chat_id']}.")
    else:
        logging.info(f"Для чата {data['chat_id']} нет анализа для сохранения.")


def send_analysis_result(target_chat_ids, bot_token, analysis_result):
    """
    Отправляет результат анализа в Telegram.
    """
    bot = TeleBot(BOT_TOKEN)

    chat = get_chat_name(chat_id)

    message_text = f"""Результат анализа для чата {
        chat}:\n\n{analysis_result}"""

    try:
        bot.send_message(chat_id=CHAT_ID, text=message_text)
        logging.info(f"""Результат анализа для чата {
                     chat_id} успешно отправлен.""")
    except Exception as e:
        logging.error(f"""Ошибка при отправке результата в Telegram для чата {
                      chat_id}: {e}""", exc_info=True)
    finally:
        bot.stop_bot()

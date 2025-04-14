import json
import aio_pika
from loguru import logger
from config import Settings
from app.scheduler.add_or_remove_schedules import add_schedule_job, remove_schedule_job

settings = Settings()


async def consume_schedule_events():
    connection = await aio_pika.connect_robust(settings.BROKER_DATA)
    channel = await connection.channel()
    queue = await channel.declare_queue("schedules", durable=True)

    logger.info("🎧 Запущен слушатель очереди 'schedules'")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    action = data.get("action")
                    schedule_id = data.get("schedule_id")

                    logger.debug(f"📨 Получено сообщение из очереди: {data}")

                    if not schedule_id or not action:
                        logger.warning(f"⚠️ Некорректное сообщение: {data}")
                        continue

                    if action == "add":
                        from app.database.models import ChatSchedules
                        logger.info(f"➕ Добавление задачи {schedule_id}")
                        schedule = await ChatSchedules.get(schedule_id=schedule_id).prefetch_related(
                            'chat', 'prompt', 'bot', 'company'
                        )
                        add_schedule_job(schedule)
                        logger.success(
                            f"✅ Задача {schedule_id} добавлена в планировщик.")

                    elif action == "delete":
                        logger.info(f"➖ Удаление задачи {schedule_id}")
                        try:
                            remove_schedule_job(schedule_id)
                            logger.success(
                                f"❌ Задача {schedule_id} удалена из планировщика.")
                        except Exception as e:
                            logger.warning(
                                f"⚠️ Не удалось удалить задачу {schedule_id}: {e}")

                    else:
                        logger.warning(
                            f"⚠️ Неизвестное действие '{action}' для задачи {schedule_id}")

                except Exception as e:
                    logger.error(
                        f"💥 Ошибка при обработке сообщения: {e}", exc_info=True)

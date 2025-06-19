import asyncio
import json

import aio_pika
from dotenv import load_dotenv
from loguru import logger

from app.scheduler.add_or_remove_schedules import add_schedule_job, remove_schedule_job

load_dotenv()


async def consume_schedule_events(settings):
    retry_delay = 5  # секунд
    while True:
        try:
            logger.info(f"🔌 Подключение к RabbitMQ: {settings.BROKER_DATA}")
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
                                from app.database.models import ChatSchedule

                                logger.info(f"➕ Добавление задачи {schedule_id}")
                                schedule = await ChatSchedule.get(
                                    id=schedule_id
                                ).prefetch_related("chat", "prompt", "bot")
                                add_schedule_job(schedule, settings)
                                logger.success(
                                    f"✅ Задача {schedule_id} добавлена в планировщик."
                                )

                            elif action == "delete":
                                logger.info(f"➖ Удаление задачи {schedule_id}")
                                try:
                                    remove_schedule_job(schedule_id)
                                    logger.success(
                                        f"""❌ Задача {schedule_id} 
                                        удалена из планировщика."""
                                    )
                                except Exception as e:
                                    logger.warning(
                                        f"""⚠️ Не удалось удалить 
                                        задачу {schedule_id}: {e}"""
                                    )

                            else:
                                logger.warning(
                                    f"""⚠️ Неизвестное действие '{action}' 
                                    для задачи {schedule_id}"""
                                )

                        except Exception as e:
                            logger.error(
                                f"💥 Ошибка при обработке сообщения: {e}", exc_info=True
                            )

        except aio_pika.exceptions.AMQPConnectionError as e:
            logger.error(f"🐇 Не удалось подключиться к RabbitMQ: {e}")
            logger.info(f"⏳ Повтор через {retry_delay} секунд...")
            await asyncio.sleep(retry_delay)
        except Exception as e:
            logger.exception(f"🔥 Непредвиденная ошибка в consumer-е: {e}")
            await asyncio.sleep(retry_delay)

import json
import aio_pika
from config import Settings

settings = Settings()


async def publish_schedule_event(schedule_id: str, action: str = "add"):
    connection = await aio_pika.connect_robust(settings.BROKER_DATA)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({
                    "action": action,
                    "schedule_id": str(schedule_id),
                }).encode()
            ),
            routing_key="schedules",
        )

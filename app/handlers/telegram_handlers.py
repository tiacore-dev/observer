from loguru import logger
from app.handlers.db_handlers import handle_message_info
from app.database.models import Bots, Messages


async def process_update(data: dict, bot: Bots):
    try:
        message = None
        edited = None

        if data.get("message"):
            message = data["message"]
            edited = False
        elif data.get("edited_message"):
            message = data["edited_message"]
            edited = True

        if not message:
            logger.warning("⚠️ Нет сообщения в апдейте")
            return

        user_account = message["from"]
        message_chat = message["chat"]

        logger.info(
            f"💬 Сообщение от @{user_account.get('username')} в {message_chat.get('title')} ({message_chat.get('id')})")

        if message_chat["type"] in ["channel", "private"]:
            logger.debug("⏭ Пропущен тип чата:", message_chat["type"])
            return

        account, chat = await handle_message_info(user_account, message_chat, bot)
        message_id = f"{chat.chat_id}_{message['message_id']}"

        if edited:
            message_obj = await Messages.filter(message_id=message_id).first()
            if message_obj:
                message_obj.text = message.get('text')
                await message_obj.save()
                logger.info(f"✏️ Сообщение {message_id} обновлено")
            else:
                logger.warning(
                    f"🧐 Попытка обновить несуществующее сообщение: {message_id}")
        else:
            await Messages.create(
                message_id=message_id,
                account=account,
                chat=chat,
                text=message.get('text')
            )
            logger.info(f"📥 Сообщение {message_id} сохранено")

    except Exception as e:
        logger.exception(f"🔥 Ошибка в process_update: {e}")

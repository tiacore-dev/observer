from loguru import logger
from app.handlers.db_handlers import handle_message_info
from app.handlers.telegram_api_url_handlers import get_file
from app.database.models import Bots, Messages
from app.s3.s3_manager import AsyncS3Manager


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
        s3_key = await put_file_to_s3(message, bot, chat.chat_id)
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
                text=message.get('text'),
                s3_key=s3_key
            )
            logger.info(f"📥 Сообщение {message_id} сохранено")

    except Exception as e:
        logger.exception(f"🔥 Ошибка в process_update: {e}")


async def put_file_to_s3(message, bot, chat_id):
    file_bytes = None
    file_name = None
    s3_key = None
    if message.get('photo'):
        smallest_photo = min(
            message["photo"], key=lambda p: p["file_size"])
        file_id = smallest_photo["file_id"]
        file_bytes, file_path = await get_file(bot.bot_token, file_id)
        file_name = file_path.split('/')[-1]

    if file_bytes and file_name:
        manager = AsyncS3Manager()
        s3_key = await manager.upload_bytes(file_bytes, chat_id, file_name)

    return s3_key

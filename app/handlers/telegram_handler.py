from loguru import logger

from app.database.models import Bot, Message
from app.handlers.db_handler import handle_message_info
from app.handlers.telegram_api_url_handlers import get_file
from app.s3.s3_manager import AsyncS3Manager
from app.yandex_funcs.yandex_funcs import transcribe_audio


async def process_update(data: dict, bot: Bot, settings):
    try:
        message = None
        edited = None
        logger.debug(f"Пришло сообщение: {data}")
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
            f"""💬 Сообщение от @{user_account.get("username")} в
              {message_chat.get("title")} ({message_chat.get("id")})"""
        )

        if message_chat["type"] in ["channel", "private"]:
            logger.debug(f"⏭ Пропущен тип чата: {message_chat['type']}")
            return

        account, chat = await handle_message_info(user_account, message_chat, bot)
        text = message.get("text")
        if message.get("voice"):
            file_id = message["voice"]["file_id"]
            result = await get_file(bot.bot_token, file_id)
            if result is None:
                logger.warning(f"⚠️ Не удалось получить файл по file_id {file_id}")
                return  # или continue, или text = "", если хочешь всё равно сохранить

            voice_bytes, _ = result

            text = await transcribe_audio(voice_bytes, "ogg", settings)
        s3_key = await put_file_to_s3(message, bot, chat.id)

        message_id = f"{chat.id}_{message['message_id']}"

        if edited:
            message_obj = await Message.filter(id=message_id).first()
            if message_obj:
                message_obj.text = text or message_obj.text
                await message_obj.save()
                logger.info(f"✏️ Сообщение {message_id} обновлено")
            else:
                logger.warning(f"🧐 Попытка обновить несуществующее сообщение: {message_id}")
        else:
            await Message.create(
                id=message_id,
                account=account,
                chat=chat,
                text=text,
                s3_key=s3_key,
            )
            logger.info(f"📥 Сообщение {message_id} сохранено")

    except Exception as e:
        logger.exception(f"🔥 Ошибка в process_update: {e}")


async def put_file_to_s3(message, bot: Bot, chat_id):
    file_bytes = None
    file_name = None
    s3_key = None
    file_id = None
    if message.get("photo"):
        smallest_photo = min(message["photo"], key=lambda p: p["file_size"])
        file_id = smallest_photo["file_id"]

    if message.get("document"):
        file_id = message["document"]["file_id"]
        file_name = message["document"]["file_name"]

    if file_id:
        result = await get_file(bot.bot_token, file_id)
        if result:
            file_bytes, file_path = result
            if not file_name:
                file_name = file_path.split("/")[-1]

        if not file_name:
            file_name = file_path.split("/")[-1]

    if file_bytes and file_name:
        manager = AsyncS3Manager()
        s3_key = await manager.upload_bytes(file_bytes, chat_id, file_name)

    return s3_key

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

        message = data.get("message") or data.get("edited_message")
        edited = "edited_message" in data

        if not message:
            logger.warning("⚠️ Нет сообщения в апдейте")
            return

        user_account = message.get("from") or {}
        message_chat = message.get("chat") or {}

        logger.info(
            f"""💬 Сообщение от @{user_account.get("username")} в
              {message_chat.get("title")} ({message_chat.get("id")})"""
        )

        if message_chat.get("type") in {"channel", "private"}:
            logger.debug(f"⏭ Пропущен тип чата: {message_chat.get('type')}")
            return

        account, chat = await handle_message_info(user_account, message_chat, bot)
        text = message.get("text")

        voice = message.get("voice")
        if voice:
            file_id = voice.get("file_id")
            if file_id:
                result = await get_file(bot.bot_token, file_id)
                if result is None:
                    logger.warning(f"⚠️ Не удалось получить файл по file_id {file_id}")
                    return

                voice_bytes, _ = result
                text = await transcribe_audio(voice_bytes, "ogg", settings)
        if not chat:
            raise ValueError
        s3_key = await put_file_to_s3(message, bot, chat.id)
        message_id = f"{chat.id}_{message.get('message_id')}"

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


async def put_file_to_s3(message: dict, bot: Bot, chat_id: int):
    file_bytes = None
    file_name = None
    s3_key = None
    file_id = None
    file_path = None

    photo_list = message.get("photo")
    if photo_list:
        smallest_photo = min(photo_list, key=lambda p: p.get("file_size", 0))
        file_id = smallest_photo.get("file_id")

    document = message.get("document")
    if document:
        file_id = document.get("file_id")
        file_name = document.get("file_name")

    if file_id:
        result = await get_file(bot.bot_token, file_id)
        if result:
            file_bytes, file_path = result
            if not file_name and file_path:
                file_name = file_path.split("/")[-1]

    if file_bytes and file_name:
        manager = AsyncS3Manager()
        s3_key = await manager.upload_bytes(file_bytes, chat_id, file_name)

    return s3_key

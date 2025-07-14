from loguru import logger

from app.database.models import (
    Account,
    AccountCompanyRelation,
    Bot,
    BotChatRelation,
    Chat,
)


async def handle_message_info(user_account: dict, message_chat: dict, bot: Bot):
    try:
        user_id = user_account.get("id")
        username = user_account.get("username")
        first_name = user_account.get("first_name")
        last_name = user_account.get("last_name")

        if not user_id or not first_name:
            logger.warning(f"⚠️ Неполные данные об аккаунте: {user_account}")
            return None, None

        account = await Account.get_or_none(id=user_id)
        if not account:
            full_name = first_name
            if last_name:
                full_name += f" {last_name}"

            account = await Account.create(
                id=user_id,
                username=full_name,
                name=username,
            )
            logger.debug(f"🆕 Новый аккаунт: @{account.name} (ID: {account.id})")

        _, acc_rel_created = await AccountCompanyRelation.get_or_create(account=account, company_id=bot.company_id)
        if acc_rel_created:
            logger.info(f"📎 Связь аккаунта с компанией создана: {account.id} ↔ {bot.id}")

        chat_id = message_chat.get("id")
        chat_title = message_chat.get("title")

        if not chat_id or not chat_title:
            logger.warning(f"⚠️ Неполные данные о чате: {message_chat}")
            return account, None

        chat = await Chat.get_or_none(id=chat_id)
        if not chat:
            chat = await Chat.create(id=chat_id, name=chat_title)
            logger.debug(f"🆕 Новый чат: {chat.name} (ID: {chat.id})")

        _, bot_chat_rel_created = await BotChatRelation.get_or_create(chat=chat, bot=bot)
        if bot_chat_rel_created:
            logger.info(f"🤖 Связь бота с чатом создана: {bot.id} ↔ {chat.id}")

        return account, chat

    except Exception as e:
        logger.exception(
            f"""❌ Ошибка в handle_message_info: user_id={user_account.get("id")} 
            | chat_id={message_chat.get("id")} | {e}"""
        )
        raise

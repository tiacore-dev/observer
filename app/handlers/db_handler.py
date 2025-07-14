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
        account = await Account.get_or_none(id=user_account["id"])
        if not account:
            name = user_account["first_name"]
            if user_account.get("last_name"):
                name += f" {user_account['last_name']}"
            account = await Account.create(
                id=user_account["id"],
                username=name,
                name=user_account["username"],
            )
            logger.debug(f"🆕 Новый аккаунт: @{account.name} (ID: {account.id})")

        _, acc_rel_created = await AccountCompanyRelation.get_or_create(account=account, company_id=bot.company_id)
        if acc_rel_created:
            logger.info(f"📎 Связь аккаунта с компанией создана: {account.id} ↔ {bot.id}")

        chat = await Chat.get_or_none(id=message_chat["id"])
        if not chat:
            chat = await Chat.create(id=message_chat["id"], name=message_chat["title"])
            logger.debug(f"🆕 Новый чат: {chat.name} (ID: {chat.id})")

        _, bot_chat_rel_created = await BotChatRelation.get_or_create(chat=chat, bot=bot)
        if bot_chat_rel_created:
            logger.info(f"🤖 Связь бота с чатом создана: {bot.id} ↔ {chat.id}")

        return account, chat

    except Exception as e:
        logger.exception(
            f"""❌ Ошибка в handle_message_info для user_id={user_account.get("id")} 
            | chat_id={message_chat.get("id")}: {e}"""
        )
        raise

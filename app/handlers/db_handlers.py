from loguru import logger
from app.database.models import Accounts, AccountCompanyRelations, Chats, BotChatRelations, Bots


async def handle_message_info(user_account: dict, message_chat: dict, bot: Bots):
    try:
        account = await Accounts.get_or_none(account_id=user_account['id'])
        if not account:
            name = user_account['first_name']
            if user_account.get('last_name'):
                name += f" {user_account['last_name']}"
            account = await Accounts.create(
                account_id=user_account['id'],
                username=name,
                account_name=user_account['username']
            )
            logger.debug(
                f"🆕 Новый аккаунт: @{account.account_name} (ID: {account.account_id})")

        _, acc_rel_created = await AccountCompanyRelations.get_or_create(
            account=account,
            company=bot.company
        )
        if acc_rel_created:
            logger.info(
                f"📎 Связь аккаунта с компанией создана: {account.account_id} ↔ {bot.company_id}")

        chat = await Chats.get_or_none(chat_id=message_chat['id'])
        if not chat:
            chat = await Chats.create(
                chat_id=message_chat['id'],
                chat_name=message_chat['title']
            )
            logger.debug(f"🆕 Новый чат: {chat.chat_name} (ID: {chat.chat_id})")

        _, bot_chat_rel_created = await BotChatRelations.get_or_create(
            chat=chat,
            bot=bot
        )
        if bot_chat_rel_created:
            logger.info(
                f"🤖 Связь бота с чатом создана: {bot.bot_id} ↔ {chat.chat_id}")

        return account, chat

    except Exception as e:
        logger.exception(
            f"❌ Ошибка в handle_message_info для user_id={user_account.get('id')} | chat_id={message_chat.get('id')}: {e}")
        raise

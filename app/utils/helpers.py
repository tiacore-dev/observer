from app.database.models import Message


async def get_messages_for_company(company_id, **filters):
    return await Message.filter(chat__company=company_id, **filters)

import html
import re
import unicodedata
from uuid import UUID

from fastapi import HTTPException
from loguru import logger
from pydantic import UUID4


def sanitize_input(value: str, max_length: int = 255) -> str:
    """Очистка строки от XSS, пробелов, html-сущностей, невидимых символов и подмен"""
    if not isinstance(value, str):
        return value

    # 1. HTML entities → символы
    value = html.unescape(value)

    # 2. Удаление HTML-тегов
    value = re.sub(r"<[^>]*>", "", value)

    # 3. Удаление очевидных XSS-паттернов
    value = re.sub(r"(?i)(javascript:|data:|vbscript:|on\w+=)", "", value)
    value = value.replace("alert", "")

    # 4. Unicode нормализация (на всякий случай)
    value = unicodedata.normalize("NFC", value)

    # 5. Удаление невидимых символов (например, управляющие)
    value = "".join(c for c in value if unicodedata.category(c) not in ["Cc", "Cf"])

    # 7. Обрезаем до max_length
    if len(value) > max_length:
        value = value[:max_length]

    return value


def normalize_form_field(value, target_type):
    if isinstance(value, str) and value.strip() == "":
        return None
    if target_type is int:
        return int(value) if value is not None else None
    if target_type == UUID4:
        return UUID(value) if value is not None else None
    return value


async def validate_exists(model_cls, id_value, field_name: str):
    if id_value is None:
        return None
    if not await model_cls.exists(id=id_value):
        raise HTTPException(status_code=400, detail=f"{field_name} не найден")
    return id_value


# если ещё не импортировано


def check_company_access(
    object_company_id,
    context: dict,
    *,
    raise_exception: bool = True,
) -> bool:
    """
    Проверяет доступ пользователя к объекту по company_id.
    Возвращает True/False или бросает 403.
    """
    if context.get("is_superadmin"):
        return True

    expected_id = str(object_company_id)
    actual_id = str(context.get("company_id"))

    if expected_id != actual_id:
        logger.warning(
            f"""❌ Проверка доступа к компании не прошла: 
            ожидалось {expected_id}, в контексте {actual_id}. """
            f"""Суперадмин: {context.get("is_superadmin")}, 
            Пользователь: {context.get("user_id")}"""
        )

        if raise_exception:
            raise HTTPException(
                status_code=403, detail="Недостаточно прав для компании"
            )
        return False

    return True

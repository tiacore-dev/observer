import uuid
from time import time
from enum import Enum
import bcrypt
from tortoise import fields
from tortoise.models import Model

# Роли пользователей


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserRole(Model):

    role_id = fields.CharEnumField(UserRoleEnum, pk=True, max_length=50)
    role_name = fields.CharField(max_length=50, unique=True)

    class Meta:
        table = "user_roles"

# Пользователи


class AdminUser(Model):
    admin_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    username = fields.CharField(max_length=50, unique=True)
    role = fields.ForeignKeyField("models.UserRole", related_name="admins")
    company = fields.ForeignKeyField("models.Company", related_name="admins")
    password_hash = fields.CharField(max_length=255)
    created_at = fields.BigIntField(default=lambda: int(time()))

    class Meta:
        table = "admin_users"

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()

    @classmethod
    async def create_admin(cls, username, role, company, password):
        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()
        admin = await cls.create(
            username=username,
            role=role,
            company=company,
            password_hash=password_hash
        )
        return admin


class User(Model):
    user_id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=255, null=True)
    account_name = fields.CharField(max_length=255, null=True)
    role = fields.ForeignKeyField("models.UserRole", related_name="users")
    company = fields.ForeignKeyField("models.Company", related_name="users")
    created_at = fields.BigIntField(default=lambda: int(time()))

    class Meta:
        table = "users"

# Аккаунты пользователей на платформах


class Company(Model):
    company_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company_name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    class Meta:
        table = "companies"


class Chat(Model):

    # Уникальный идентификатор чата
    chat_id = fields.BigIntField(pk=True)
    chat_name = fields.CharField(max_length=255, null=True)
    default_prompt = fields.ForeignKeyField(
        "models.Prompt", related_name="chats", null=True)
    created_at = fields.BigIntField(default=lambda: int(time()))
    company = fields.ForeignKeyField("models.Company", related_name="chats")

    class Meta:
        table = "chats"


class ChatSchedule(Model):
    schedule_id = fields.IntField(pk=True)

    chat = fields.ForeignKeyField("models.Chat", related_name="schedules")
    prompt = fields.ForeignKeyField(
        "models.Prompt",
        related_name="schedules"
    )

    # 'interval', 'daily_time', 'cron', 'once'
    schedule_type = fields.CharField(max_length=20)

    # --- Тип: interval ---
    interval_hours = fields.IntField(null=True)
    interval_minutes = fields.IntField(null=True)

    # --- Тип: daily_time ---
    time_of_day = fields.TimeField(null=True)  # типа 05:00 каждый день

    # --- Тип: cron ---
    cron_expression = fields.CharField(
        max_length=100, null=True)  # '0 5 * * *'

    # --- Тип: once ---
    run_at = fields.DatetimeField(null=True)

    # Общие поля:
    enabled = fields.BooleanField(default=False)
    last_run_at = fields.DatetimeField(null=True)

    created_at = fields.BigIntField(default=lambda: int(time()))

    class Meta:
        table = "chat_schedules"


class BotInfo(Model):
    bot_id = fields.BigIntField(pk=True)
    bot_token = fields.CharField(max_length=255)
    bot_name = fields.CharField(max_length=255)
    target_chat_id = fields.ForeignKeyField(
        "models.Chat", related_name="bot", null=True)
    company = fields.ForeignKeyField("models.Company", related_name="bots")
    is_active = fields.BooleanField(default=True)
    created_at = fields.BigIntField(default=lambda: int(time()))

    class Meta:
        table = "bots"


class AnalysisResult(Model):

    analysis_id = fields.UUIDField(pk=True, default=uuid.uuid4)

    prompt = fields.ForeignKeyField("models.Prompt", related_name="analysis")
    result_text = fields.TextField()
    schedule = fields.ForeignKeyField(
        "models.ChatSchedule",
        related_name="analysis_results",
        null=True
    )
    company = fields.ForeignKeyField("models.Company", related_name="analysis")
    created_at = fields.BigIntField(default=lambda: int(time()))

    # Разворачиваем фильтры:
    date_from = fields.BigIntField(null=True)
    date_to = fields.BigIntField(null=True)
    user = fields.ForeignKeyField(
        "models.User", related_name="analysis_results", null=True)
    chat = fields.ForeignKeyField(
        "models.Chat", related_name="analysis_results", null=True)

    tokens_input = fields.IntField()
    tokens_output = fields.IntField()

    class Meta:
        table = "analysis_results"


class Message(Model):

    message_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    timestamp = fields.BigIntField(default=lambda: int(time()))
    user = fields.ForeignKeyField("models.User", related_name="messages")
    # Идентификатор чата (64-битное число)
    chat = fields.ForeignKeyField("models.Chat", related_name="messages")
    text = fields.TextField(null=True)
    s3_key = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "messages"


class Prompt(Model):

    prompt_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    prompt_name = fields.CharField(max_length=255)
    text = fields.TextField()
    use_automatic = fields.BooleanField(null=True, default=False)
    company = fields.ForeignKeyField("models.Company", related_name="prompts")
    created_at = fields.BigIntField(default=lambda: int(time()))

    class Meta:
        table = "prompts"

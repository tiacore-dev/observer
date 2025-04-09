import uuid
import bcrypt
from tortoise import fields
from tortoise.models import Model

# Роли пользователей


class UserRoles(Model):

    role_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    role_name = fields.CharField(max_length=50, unique=True)

    def __repr__(self):
        return f"<UserRoles(role_id={self.role_id}, role_name='{self.role_name}')>"

    class Meta:
        table = "user_roles"


class Permissions(Model):
    permission_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    role = fields.ForeignKeyField(
        "diff_models.UserRoles", related_name="permissions")

    def __repr__(self):
        return f"<Permissions(permission_id={self.permission_id}, role={self.role.role_id})>"

    class Meta:
        table = "permissions"

# Пользователи


class Companies(Model):
    company_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company_name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    def __repr__(self):
        return f"<Companies(company_id='{self.company_id}', name='{self.company_name}')>"

    class Meta:
        table = "companies"


class Users(Model):
    user_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())

    def __repr__(self):
        return f"<Users(user_id={self.user_id}, username='{self.username}')>"

    class Meta:
        table = "users"

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()

    @classmethod
    async def create_user(cls, username, password):
        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()).decode()
        user = await cls.create(
            username=username,
            password_hash=password_hash
        )
        return user


class UserCompanyRelations(Model):
    user_company_relation_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField(
        "diff_models.Users", related_name="user_relations")
    company = fields.ForeignKeyField(
        "diff_models.Companies", related_name="user_relations")
    role = fields.ForeignKeyField(
        "diff_models.UserRoles", related_name="user_relations")

    def __repr__(self):
        return f"<UserCompanyRelations(user={self.user.user_id}, company={self.company.company_id}, role={self.role.role_id})>"

    class Meta:
        table = "user_company_relations"


class Accounts(Model):
    account_id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=255, null=True)
    account_name = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())

    def __repr__(self):
        return f"<Accounts(account_id={self.account_id}, username='{self.username}')>"

    class Meta:
        table = "accounts"


class AccountCompanyRelations(Model):
    account_company_relation_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company = fields.ForeignKeyField(
        "diff_models.Companies", related_name="account_relations")
    account = fields.ForeignKeyField(
        "diff_models.Accounts", related_name="account_relations")

    def __repr__(self):
        return f"<AccountCompanyRelations(account={self.account.account_id}, company={self.company.company_id})>"

    class Meta:
        table = "account_company_relations"


class Chats(Model):

    # Уникальный идентификатор чата
    chat_id = fields.BigIntField(pk=True)
    chat_name = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())

    def __repr__(self):
        return f"<Chats(chat_id={self.chat_id}, name='{self.chat_name}')>"

    class Meta:
        table = "chats"


class Bots(Model):
    bot_id = fields.BigIntField(pk=True)
    bot_token = fields.CharField(max_length=255)
    secret_token = fields.CharField(max_length=255)
    bot_username = fields.CharField(max_length=255)
    bot_first_name = fields.CharField(max_length=255)
    company = fields.ForeignKeyField("diff_models.Companies", related_name="bots")
    is_active = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())

    def __repr__(self):
        return f"<Bots(bot_id={self.bot_id}, name='{self.bot_username}', active={self.is_active})>"

    class Meta:
        table = "bots"


class BotChatRelations(Model):
    bot_chat_relation_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    bot = fields.ForeignKeyField("diff_models.Bots", related_name="bot_relations")
    chat = fields.ForeignKeyField("diff_models.Chats", related_name="bot_relations")
    is_admin = fields.BooleanField(default=False)

    def __repr__(self):
        return f"<BotChatRelations(bot={self.bot.bot_id}, chat={self.chat.chat_id})>"

    class Meta:
        table = "bot_chat_relations"


class Messages(Model):

    message_id = fields.CharField(pk=True, max_length=255)
    timestamp = fields.DatetimeField(auto_now_add=True)
    account = fields.ForeignKeyField(
        "diff_models.Accounts", related_name="messages")

    chat = fields.ForeignKeyField("diff_models.Chats", related_name="messages")
    text = fields.TextField(null=True)
    s3_key = fields.CharField(max_length=255, null=True)

    @property
    def created_at_ts(self):
        return int(self.timestamp.timestamp())

    def __repr__(self):
        return f"<Messages(message_id={self.message_id}, chat={self.chat.chat_id}, account={self.account.account_id})>"

    class Meta:
        table = "messages"


class ChatSchedules(Model):
    schedule_id = fields.UUIDField(pk=True, default=uuid.uuid4)

    chat = fields.ForeignKeyField("diff_models.Chats", related_name="schedules")
    prompt = fields.ForeignKeyField(
        "diff_models.Prompts",
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
    enabled = fields.BooleanField(default=True)
    last_run_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    time_to_send = fields.BigIntField()

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())
    company = fields.ForeignKeyField(
        "diff_models.Companies", related_name="schedules")

    def __repr__(self):
        return f"<ChatSchedules(schedule_id={self.schedule_id}, chat={self.chat.chat_id}, type='{self.schedule_type}')>"

    class Meta:
        table = "chat_schedules"


class TargetChats(Model):
    target_chat_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    schedule = fields.ForeignKeyField(
        "diff_models.ChatSchedules", related_name="target_chats")
    chat = fields.ForeignKeyField("diff_models.Chats", related_name="target_chats")

    def __repr__(self):
        return f"<TargetChats(target_chat_id={self.target_chat_id}, chat={self.chat.chat_id})>"

    class Meta:
        table = "target_chats"


class AnalysisResult(Model):

    analysis_id = fields.UUIDField(pk=True, default=uuid.uuid4)

    prompt = fields.ForeignKeyField("diff_models.Prompts", related_name="analysis")
    result_text = fields.TextField()
    chat = fields.ForeignKeyField(
        "diff_models.Chats", related_name="analysis_results")
    schedule = fields.ForeignKeyField(
        "diff_models.ChatSchedules",
        related_name="analysis_results",
        null=True
    )
    company = fields.ForeignKeyField(
        "diff_models.Companies", related_name="analysis")
    created_at = fields.DatetimeField(auto_now_add=True)

    # Разворачиваем фильтры:
    date_from = fields.BigIntField()
    date_to = fields.BigIntField()

    tokens_input = fields.IntField()
    tokens_output = fields.IntField()

    send_time = fields.BigIntField(null=True)

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())

    def __repr__(self):
        return f"<AnalysisResult(analysis_id={self.analysis_id}, prompt={self.prompt.prompt_id})>"

    class Meta:
        table = "analysis_results"


class Prompts(Model):

    prompt_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    prompt_name = fields.CharField(max_length=255)
    text = fields.TextField()
    company = fields.ForeignKeyField(
        "diff_models.Companies", related_name="prompts")
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def created_at_ts(self):
        return int(self.created_at.timestamp())

    def __repr__(self):
        return f"<Prompts(prompt_id={self.prompt_id}, name='{self.prompt_name}')>"

    class Meta:
        table = "prompts"

from tortoise import Model, fields

MAX_VERSION_LENGTH = 255


class Aerich(Model):
    version = fields.CharField(max_length=MAX_VERSION_LENGTH)
    app = fields.CharField(max_length=20)

    class Meta:
        ordering = ["-id"]


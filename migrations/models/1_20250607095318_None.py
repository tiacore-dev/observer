from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "accounts" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(255),
    "name" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "account_company_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "company_id" UUID NOT NULL,
    "account_id" BIGINT NOT NULL REFERENCES "accounts" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "bots" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "bot_token" VARCHAR(255) NOT NULL,
    "secret_token" VARCHAR(255) NOT NULL,
    "bot_username" VARCHAR(255) NOT NULL,
    "bot_first_name" VARCHAR(255) NOT NULL,
    "company_id" UUID NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "comment" TEXT
);
CREATE TABLE IF NOT EXISTS "chats" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "bot_chat_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "is_admin" BOOL NOT NULL DEFAULT False,
    "bot_id" BIGINT NOT NULL REFERENCES "bots" ("id") ON DELETE CASCADE,
    "chat_id" BIGINT NOT NULL REFERENCES "chats" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "messages" (
    "id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "text" TEXT,
    "s3_key" VARCHAR(255),
    "account_id" BIGINT NOT NULL REFERENCES "accounts" ("id") ON DELETE CASCADE,
    "chat_id" BIGINT NOT NULL REFERENCES "chats" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "prompts" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "text" TEXT NOT NULL,
    "company_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "chat_schedules" (
    "id" UUID NOT NULL PRIMARY KEY,
    "schedule_type" VARCHAR(20) NOT NULL,
    "interval_hours" INT,
    "interval_minutes" INT,
    "time_of_day" TIMETZ,
    "cron_expression" VARCHAR(100),
    "run_at" TIMESTAMPTZ,
    "enabled" BOOL NOT NULL DEFAULT True,
    "last_run_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "send_strategy" VARCHAR(10) NOT NULL DEFAULT 'fixed',
    "send_after_minutes" INT,
    "time_to_send" TIMETZ,
    "company_id" UUID NOT NULL,
    "bot_id" BIGINT NOT NULL REFERENCES "bots" ("id") ON DELETE CASCADE,
    "chat_id" BIGINT NOT NULL REFERENCES "chats" ("id") ON DELETE CASCADE,
    "prompt_id" UUID NOT NULL REFERENCES "prompts" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "analysis_results" (
    "id" UUID NOT NULL PRIMARY KEY,
    "result_text" TEXT NOT NULL,
    "company_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "date_from" TIMESTAMPTZ NOT NULL,
    "date_to" TIMESTAMPTZ NOT NULL,
    "tokens_input" INT NOT NULL,
    "tokens_output" INT NOT NULL,
    "send_time" BIGINT,
    "chat_id" BIGINT NOT NULL REFERENCES "chats" ("id") ON DELETE CASCADE,
    "prompt_id" UUID NOT NULL REFERENCES "prompts" ("id") ON DELETE CASCADE,
    "schedule_id" UUID REFERENCES "chat_schedules" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "target_chats" (
    "id" UUID NOT NULL PRIMARY KEY,
    "chat_id" BIGINT NOT NULL REFERENCES "chats" ("id") ON DELETE CASCADE,
    "schedule_id" UUID NOT NULL REFERENCES "chat_schedules" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

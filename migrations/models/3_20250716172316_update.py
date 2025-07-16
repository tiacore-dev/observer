from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat_schedules" ADD "schedule_strategy" VARCHAR(12) NOT NULL DEFAULT 'analysis';
        ALTER TABLE "chat_schedules" ADD "notification_text" TEXT;
        ALTER TABLE "chat_schedules" ALTER COLUMN "prompt_id" DROP NOT NULL;
        ALTER TABLE "chat_schedules" ALTER COLUMN "send_strategy" DROP NOT NULL;
        ALTER TABLE "chat_schedules" ALTER COLUMN "send_strategy" TYPE VARCHAR(8) USING "send_strategy"::VARCHAR(8);
        ALTER TABLE "chat_schedules" ALTER COLUMN "schedule_type" TYPE VARCHAR(10) USING "schedule_type"::VARCHAR(10);
        ALTER TABLE "chat_schedules" ALTER COLUMN "chat_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat_schedules" DROP COLUMN "schedule_strategy";
        ALTER TABLE "chat_schedules" DROP COLUMN "notification_text";
        ALTER TABLE "chat_schedules" ALTER COLUMN "prompt_id" SET NOT NULL;
        ALTER TABLE "chat_schedules" ALTER COLUMN "send_strategy" TYPE VARCHAR(10) USING "send_strategy"::VARCHAR(10);
        ALTER TABLE "chat_schedules" ALTER COLUMN "send_strategy" SET NOT NULL;
        ALTER TABLE "chat_schedules" ALTER COLUMN "schedule_type" TYPE VARCHAR(20) USING "schedule_type"::VARCHAR(20);
        ALTER TABLE "chat_schedules" ALTER COLUMN "chat_id" SET NOT NULL;"""

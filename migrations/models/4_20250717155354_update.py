from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat_schedules" DROP COLUMN "run_at";
        ALTER TABLE "chat_schedules" DROP COLUMN "time_of_day";
        ALTER TABLE "chat_schedules" ALTER COLUMN "schedule_type" TYPE VARCHAR(8) USING "schedule_type"::VARCHAR(8);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat_schedules" ADD "run_at" TIMESTAMPTZ;
        ALTER TABLE "chat_schedules" ADD "time_of_day" TIMETZ;
        ALTER TABLE "chat_schedules" ALTER COLUMN "schedule_type" TYPE VARCHAR(10) USING "schedule_type"::VARCHAR(10);"""

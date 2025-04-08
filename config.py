import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://db.sqlite3")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')

    allowed_hosts_raw = os.getenv("ALLOWED_HOSTS", "*")
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_raw.split(",")]

    # LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_LEVEL = "DEBUG"
    ALGORITHM = "HS256"
    PORT = os.getenv('PORT')

    JWT_SECRET = os.getenv('JWT_SECRET')
    ENDPOINT_URL = os.getenv('ENDPOINT_URL')
    REGION_NAME = os.getenv('REGION_NAME')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL')
    # Константы API
    YANDEX_SPEECHKIT_API_URL = os.getenv('YANDEX_SPEECHKIT_API_URL')
    YANDEX_GPT_API_URL = os.getenv('YANDEX_GPT_API_URL')

    # Токен и ID каталога
    YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
    FOLDER_ID = os.getenv('FOLDER_ID')

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

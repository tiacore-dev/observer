import patch
from celery import Celery
from config import Settings

settings = Settings()

celery_app = Celery(
    "observer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.celery.tasks"],  # Импортируемый путь к таскам
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

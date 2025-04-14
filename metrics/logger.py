import sys
import logging
from loguru import logger
from prometheus_client import Counter

# 📊 Prometheus counters
error_counter = Counter("fastapi_errors_total",
                        "Total number of FastAPI errors")
error_counter_by_user = Counter(
    "fastapi_errors_total_by_user",
    "Total number of errors per user",
    ["user_id", "login", "role"]
)


# 📈 Prometheus hook — простой, без user_id
def prometheus_hook(message):
    record = message.record
    if record["level"].no >= 40:  # 40 = ERROR
        error_counter.inc()
        try:
            error_counter_by_user.labels(
                user_id="unknown",
                login="system",
                role="system"
            ).inc()
        except Exception as e:
            print(f"[PrometheusHook] Ошибка при инкременте метрик: {e}")


# 🧲 InterceptHandler для stdlib логгера
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(
            level, record.getMessage())


# 🛠 Основная настройка логгера
def setup_logger():
    # 🔌 Перехватываем стандартный логгер
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

    # 🔊 Перехватываем uvicorn/gunicorn
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn", "gunicorn.error"):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False

    logger.remove()

    logger.add(
        sys.stdout,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | "
               "<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        colorize=True,
    )

    logger.add(
        "logs/app.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {function}:{line} - {message}",
        enqueue=True,
    )

    logger.add(prometheus_hook, level="ERROR")

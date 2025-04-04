from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from tortoise.queryset import Prefetch
from loguru import logger
from config import Settings
from app.database.models import Users, UserCompanyRelations
from app.auth_schemas import bearer_scheme

# Конфигурация JWT
settings = Settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DAYS = int(settings.REFRESH_TOKEN_EXPIRE_DAYS)


# Создание токена


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # logger.info(f"Created Access JWT: {encoded_jwt}")
    return encoded_jwt

# Проверка токена


def create_refresh_token(data: dict):
    return create_access_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


async def get_current_admin(username: str) -> Users:
    user = await Users.filter(username=username).prefetch_related(
        Prefetch("user_relations", queryset=UserCompanyRelations.all(
        ).prefetch_related("company"))
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> str:
    """
    Проверяет токен из заголовка Authorization и возвращает имя пользователя.
    """
    if credentials is None:
        logger.warning("❌ Запрос без токена! Отправляем 401")
        raise HTTPException(status_code=401, detail="Missing token")

    if not credentials.credentials:
        logger.warning("❌ Пустой токен! Отправляем 401")
        raise HTTPException(status_code=401, detail="Empty token")

    token = credentials.credentials
    logger.debug(f"🔍 Проверяем токен: {token}")

    username = verify_token(token)
    user = await get_current_admin(username)
    return user


def verify_token(token: str) -> str:
    # logger.info(f"Проверка токена: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Некорректный токен: отсутствует sub")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        # logger.success(f"Токен валиден, username: {username}")
        return username
    except JWTError as exc:
        logger.error("Ошибка JWT-декодирования")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


async def login_handler(username: str, password: str):
    user = await Users.filter(username=username).first()

    if not user:
        return None  # Возвращаем None, если пользователь не найден

    check_password = user.check_password(password)
    if check_password:
        return user

    return None  # Возвращаем None, если пароль неверный

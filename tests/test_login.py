import json
import pytest


@pytest.mark.usefixtures("seed_admin")
@pytest.mark.asyncio
async def test_login_success(test_app):
    """Проверяем успешную аутентификацию."""
    response = await test_app.post(
        "/auth/token",
        json={"username": "admin", "password": "qweasdzcx"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data


@pytest.mark.asyncio
async def test_refresh_token_success(test_app, jwt_token_admin):
    """Проверяем, что refresh-токен можно обменять на новый access-токен."""
    response = await test_app.post(
        "/auth/refresh", data=json.dumps({"refresh_token": jwt_token_admin["refresh_token"]}))

    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data


@pytest.mark.asyncio
async def test_login_failure(test_app):
    """Проверяем неудачную аутентификацию с неправильным паролем."""
    response = await test_app.post(
        "/auth/token",
        json={"username": "test_user", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверные учетные данные"


@pytest.mark.asyncio
async def test_refresh_token_invalid(test_app):
    """Проверяем обновление токена с неверным refresh-токеном."""
    response = await test_app.post(
        "/auth/refresh", data=json.dumps({"refresh_token": "invalid_token"}))

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный или просроченный токен"

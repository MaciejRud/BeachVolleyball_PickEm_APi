"""
Tests for security features API.
"""

import pytest

from httpx import AsyncClient
from pickemApi.models.model import User
from pickemApi.models.usermanager import UserManager
from pickemApi.config import config


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    """Test registration of a new user."""
    user_data = {
        "email": "testuser1@example.com",
        "password": "strongpassword",
        "username": "testuser",
    }

    response = await async_client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    response_json = response.json()
    assert response_json["email"] == user_data["email"]
    assert "id" in response_json


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: User):
    """Test user login."""
    login_data = {
        "username": registered_user.email,  # Użyj e-maila jako loginu
        "password": "strongpassword",
    }

    response = await async_client.post("/auth/jwt/login", data=login_data)
    assert response.status_code == 200  # Logowanie powiodło się

    # Sprawdź, czy token JWT został zwrócony
    token = response.json()["access_token"]
    assert token


@pytest.mark.anyio
async def test_reset_password(async_client: AsyncClient, registered_user: User, mocker):
    """Test password reset request."""
    # Zakładając, że użytkownik już istnieje
    spy = mocker.spy(UserManager, "on_after_forgot_password")
    reset_data = {"email": registered_user.email}

    response = await async_client.post("/auth/forgot-password", json=reset_data)
    assert response.status_code == 202  # Wysłano e-mail do zresetowania hasła

    # Resetowanie hasła za pomocą tokena
    token = spy.call_args[0][2]
    print(token)
    new_password_data = {"token": token, "password": "newstrongpassword"}

    response = await async_client.post("/auth/reset-password", json=new_password_data)
    assert response.status_code == 200  # Hasło zostało zresetowane


@pytest.mark.anyio
async def test_endpoint_with_authentication(authorized_client: AsyncClient):
    """Test for access to endpoint required authentication."""
    res = await authorized_client.get("/authenticated-route")

    assert res.status_code == 200

    assert "message" in res.json()

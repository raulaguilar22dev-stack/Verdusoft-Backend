"""Tests de integracion para JWT auth y autorizacion por roles."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.auth.dependencies import get_current_user, require_admin, get_current_user_optional


@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_token_valido_admin(self, admin_token):
        user = await get_current_user(f"Bearer {admin_token}")
        assert user["id"] == "admin-user-123"
        assert user["role"] == "admin"
        assert user["email"] == "admin@test.com"

    async def test_token_valido_publico(self, public_token):
        user = await get_current_user(f"Bearer {public_token}")
        assert user["role"] == "public"

    async def test_sin_token(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)
        assert exc_info.value.status_code == 401
        assert "Falta el header Authorization" in exc_info.value.detail

    async def test_formato_invalido(self, admin_token):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(f"Basic {admin_token}")
        assert exc_info.value.status_code == 401
        assert "Formato de Authorization invalido" in exc_info.value.detail

    async def test_token_expirado(self, expired_token):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(f"Bearer {expired_token}")
        assert exc_info.value.status_code == 401
        assert "Token expirado" in exc_info.value.detail

    async def test_token_invalido(self, invalid_token):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(f"Bearer {invalid_token}")
        assert exc_info.value.status_code == 401
        assert "Token invalido" in exc_info.value.detail


@pytest.mark.asyncio
class TestRequireAdmin:
    async def test_admin_permitido(self, admin_token):
        user = await require_admin(f"Bearer {admin_token}")
        assert user["role"] == "admin"

    async def test_publico_denegado(self, public_token):
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(f"Bearer {public_token}")
        assert exc_info.value.status_code == 403
        assert "administrador" in exc_info.value.detail


@pytest.mark.asyncio
class TestGetCurrentUserOptional:
    async def test_con_token_valido(self, admin_token):
        user = await get_current_user_optional(f"Bearer {admin_token}")
        assert user is not None
        assert user["role"] == "admin"

    async def test_sin_token(self):
        user = await get_current_user_optional(None)
        assert user is None

    async def test_con_token_invalido(self, invalid_token):
        user = await get_current_user_optional(f"Bearer {invalid_token}")
        assert user is None

    async def test_con_token_expirado(self, expired_token):
        user = await get_current_user_optional(f"Bearer {expired_token}")
        assert user is None

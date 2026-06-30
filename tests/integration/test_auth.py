"""Tests de integracion para el router de autenticacion (/api/auth/register)."""

from __future__ import annotations

from unittest.mock import patch, AsyncMock

import httpx
import pytest


class FakeResponse:
    """Mock de respuesta httpx."""

    def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self) -> dict:
        return self._json


def _mock_httpx_post(mock_cls, response: FakeResponse, side_effect=None):
    """Configura el mock de httpx.AsyncClient para devolver una respuesta fija."""
    mock_instance = AsyncMock()
    mock_cls.return_value.__aenter__.return_value = mock_instance
    if side_effect:
        mock_instance.post.side_effect = side_effect
    else:
        mock_instance.post.return_value = response
    return mock_instance


class TestRegistrarAdmin:
    def test_registro_exitoso(self, client):
        with patch("app.routers.auth.httpx.AsyncClient") as mock_cls:
            _mock_httpx_post(
                mock_cls, FakeResponse(200, {"id": "uuid-admin-123"})
            )
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "admin@test.com",
                    "password": "SecurePass123!",
                    "master_key": "master-key-de-test-2026",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["mensaje"] == "Usuario admin creado exitosamente"
        assert data["user_id"] == "uuid-admin-123"

    def test_master_key_incorrecta(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "admin@test.com",
                "password": "SecurePass123!",
                "master_key": "clave-mala",
            },
        )
        assert response.status_code == 403
        assert "Clave maestra incorrecta" in response.json()["mensaje"]

    def test_supabase_devuelve_422(self, client):
        with patch("app.routers.auth.httpx.AsyncClient") as mock_cls:
            _mock_httpx_post(
                mock_cls, FakeResponse(422, {"msg": "Invalid email format"})
            )
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "valido@test.com",
                    "password": "SecurePass123!",
                    "master_key": "master-key-de-test-2026",
                },
            )
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["mensaje"]

    def test_supabase_devuelve_400(self, client):
        with patch("app.routers.auth.httpx.AsyncClient") as mock_cls:
            _mock_httpx_post(mock_cls, FakeResponse(400, text="Email already exists"))
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "admin@test.com",
                    "password": "SecurePass123!",
                    "master_key": "master-key-de-test-2026",
                },
            )
        assert response.status_code == 400
        assert "Error al crear usuario" in response.json()["mensaje"]

    def test_error_de_conexion(self, client):
        with patch("app.routers.auth.httpx.AsyncClient") as mock_cls:
            _mock_httpx_post(
                mock_cls,
                FakeResponse(200),
                side_effect=httpx.RequestError("Connection refused"),
            )
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "admin@test.com",
                    "password": "SecurePass123!",
                    "master_key": "master-key-de-test-2026",
                },
            )
        assert response.status_code == 503
        assert "Error de conexion" in response.json()["mensaje"]

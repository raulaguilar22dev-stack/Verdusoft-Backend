"""Fixtures y utilidades compartidas para todo el suite de tests."""

from __future__ import annotations

import time
from typing import Any, Optional
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

# -----------------------------------------------------------------------------
# Constantes de test
# -----------------------------------------------------------------------------
TEST_JWT_SECRET = "test-secret-very-long-and-secure-123456789"
TEST_ADMIN_KEY = "master-key-de-test-2026"
TEST_SUPABASE_URL = "https://test.supabase.co"
TEST_SUPABASE_KEY = "test-service-role-key"
TEST_PROJECT_REF = "lscmcxxvayzdgwinpokx"

# -----------------------------------------------------------------------------
# Mock Supabase Client
# -----------------------------------------------------------------------------


class _MockResult:
    """Resultado de execute() con atributo .data."""

    def __init__(self, data: list[dict] | None):
        self.data = data


class _MockTable:
    """Query builder mock que registra la cadena de llamadas."""

    def __init__(self, client: "MockSupabase", name: str):
        self._client = client
        self._name = name
        self._chain: list[str] = [f"table:{name}"]
        self._insert_data: dict | None = None
        self._update_data: dict | None = None

    def select(self, cols: str) -> "_MockTable":
        self._chain.append(f"select:{cols}")
        return self

    def eq(self, col: str, val: Any) -> "_MockTable":
        self._chain.append(f"eq:{col}:{val}")
        return self

    def ilike(self, col: str, val: str) -> "_MockTable":
        self._chain.append(f"ilike:{col}:{val}")
        return self

    def gte(self, col: str, val: Any) -> "_MockTable":
        self._chain.append(f"gte:{col}:{val}")
        return self

    def lte(self, col: str, val: Any) -> "_MockTable":
        self._chain.append(f"lte:{col}:{val}")
        return self

    def order(self, col: str, desc: bool = False) -> "_MockTable":
        self._chain.append(f"order:{col}:{desc}")
        return self

    def range(self, start: int, end: int) -> "_MockTable":
        self._chain.append(f"range:{start}:{end}")
        return self

    def insert(self, data: dict) -> "_MockTable":
        self._chain.append("insert")
        self._insert_data = data
        return self

    def update(self, data: dict) -> "_MockTable":
        self._chain.append("update")
        self._update_data = data
        return self

    def execute(self) -> _MockResult:
        key = "|".join(self._chain)
        call_record: dict[str, Any] = {
            "type": "query",
            "key": key,
            "table": self._name,
        }
        if self._insert_data is not None:
            call_record["insert_data"] = self._insert_data
        if self._update_data is not None:
            call_record["update_data"] = self._update_data
        self._client.calls.append(call_record)

        result = self._client.responses.get(key, {"data": []})
        return _MockResult(result.get("data"))


class _MockRPC:
    def __init__(self, client: "MockSupabase", func_name: str, params: dict):
        self._client = client
        self._func_name = func_name
        self._params = params

    def execute(self) -> _MockResult:
        key = f"rpc:{self._func_name}"
        self._client.calls.append(
            {"type": "rpc", "key": key, "func": self._func_name, "params": self._params}
        )
        result = self._client.responses.get(key, {"data": []})
        return _MockResult(result.get("data"))


class MockSupabase:
    """Cliente Supabase falso para tests unitarios.

    Usar `responses` para pre-configurar retornos:
        client.responses = {
            "table:producto|select:*|eq:id_producto:1": {"data": [{"id_producto": 1}]},
            "rpc:crear_venta": {"data": [{"id_venta": 42}]},
        }
    """

    def __init__(self, responses: Optional[dict[str, dict]] = None):
        self.responses: dict[str, dict] = responses or {}
        self.calls: list[dict] = []

    def table(self, name: str) -> _MockTable:
        return _MockTable(self, name)

    def rpc(self, func_name: str, params: dict) -> _MockRPC:
        return _MockRPC(self, func_name, params)


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Asegura que todos los tests usan variables de entorno de test."""
    monkeypatch.setenv("SUPABASE_URL", TEST_SUPABASE_URL)
    monkeypatch.setenv("SUPABASE_KEY", TEST_SUPABASE_KEY)
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
    monkeypatch.setenv("ADMIN_MASTER_KEY", TEST_ADMIN_KEY)
    monkeypatch.setenv("SUPABASE_PROJECT_REF", TEST_PROJECT_REF)

    # Parchear settings YA importada (import-time caching)
    from app import config as config_module

    monkeypatch.setattr(config_module.settings, "supabase_url", TEST_SUPABASE_URL)
    monkeypatch.setattr(config_module.settings, "supabase_key", TEST_SUPABASE_KEY)
    monkeypatch.setattr(config_module.settings, "supabase_jwt_secret", TEST_JWT_SECRET)
    monkeypatch.setattr(config_module.settings, "admin_master_key", TEST_ADMIN_KEY)
    monkeypatch.setattr(config_module.settings, "supabase_project_ref", TEST_PROJECT_REF)


@pytest.fixture
def app():
    """Instancia de FastAPI con rate limiter desactivado para tests."""
    from app.main import app as fastapi_app

    # Desactivar rate limiter
    fastapi_app.state.limiter = None
    return fastapi_app


@pytest.fixture
def client(app):
    """TestClient listo para usar."""
    return TestClient(app)


@pytest.fixture
def mock_db() -> MockSupabase:
    """MockSupabase limpio (sin respuestas pre-configuradas)."""
    return MockSupabase()


@pytest.fixture
def admin_token() -> str:
    """JWT válido con rol admin."""
    now = time.time()
    payload = {
        "sub": "admin-user-123",
        "email": "admin@test.com",
        "app_metadata": {"role": "admin"},
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def public_token() -> str:
    """JWT válido con rol public."""
    now = time.time()
    payload = {
        "sub": "public-user-456",
        "email": "public@test.com",
        "app_metadata": {"role": "public"},
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def expired_token() -> str:
    """JWT expirado (hace 1 hora)."""
    now = time.time()
    payload = {
        "sub": "user-789",
        "email": "expired@test.com",
        "app_metadata": {"role": "admin"},
        "iat": now - 7200,
        "exp": now - 3600,
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def invalid_token() -> str:
    """Token malformado / firma incorrecta."""
    return "invalid.token.signature"


@pytest.fixture
def override_db(app):
    """Permite inyectar un MockSupabase como dependencia get_supabase_client."""
    from app.dependencies import get_supabase_client

    def _apply(mock_db):
        app.dependency_overrides[get_supabase_client] = lambda: mock_db

    yield _apply
    app.dependency_overrides.pop(get_supabase_client, None)

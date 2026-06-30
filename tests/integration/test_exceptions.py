"""Tests de integracion para los handlers globales de excepciones."""

from __future__ import annotations

import json

import pytest
from fastapi import HTTPException, Request

from app.exceptions import http_exception_handler, general_exception_handler


def _make_request():
    return Request(
        {
            "type": "http",
            "method": "GET",
            "url": "http://test",
            "path": "/",
            "headers": [],
        }
    )


def _json_response(response):
    return json.loads(response.body)


@pytest.mark.asyncio
class TestHttpExceptionHandler:
    async def test_maneja_404(self):
        request = _make_request()
        exc = HTTPException(status_code=404, detail="Recurso no encontrado")
        response = await http_exception_handler(request, exc)
        assert response.status_code == 404
        assert _json_response(response) == {"mensaje": "Recurso no encontrado"}

    async def test_maneja_400(self):
        request = _make_request()
        exc = HTTPException(status_code=400, detail="Datos invalidos")
        response = await http_exception_handler(request, exc)
        assert response.status_code == 400
        assert _json_response(response) == {"mensaje": "Datos invalidos"}

    async def test_no_expone_internals(self):
        request = _make_request()
        exc = HTTPException(status_code=403, detail="Acceso denegado")
        body = await http_exception_handler(request, exc)
        assert "Traceback" not in str(body.body)


@pytest.mark.asyncio
class TestGeneralExceptionHandler:
    async def test_maneja_exception_generica(self):
        request = _make_request()
        exc = RuntimeError("secret database password: abc123")
        response = await general_exception_handler(request, exc)
        assert response.status_code == 500
        json_body = _json_response(response)
        assert json_body["mensaje"] == "Error interno del servidor"
        assert "abc123" not in str(json_body)
        assert "secret" not in str(json_body)

    async def test_maneja_value_error(self):
        request = _make_request()
        exc = ValueError("algo malo paso")
        response = await general_exception_handler(request, exc)
        assert response.status_code == 500
        assert _json_response(response)["mensaje"] == "Error interno del servidor"

"""Manejadores de excepciones globales."""

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Maneja excepciones HTTP conocidas."""
    return JSONResponse(status_code=exc.status_code, content={"mensaje": exc.detail})


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Maneja excepciones no controladas.

    Nunca expone str(exc) al cliente para evitar filtrar
    internals del sistema.
    """
    logger.error(f"Error no manejado en {request.url.path}: {exc!r}")
    return JSONResponse(
        status_code=500,
        content={"mensaje": "Error interno del servidor"},
    )

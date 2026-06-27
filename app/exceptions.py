"""Manejadores de excepciones globales."""

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Maneja excepciones HTTP conocidas."""
    return JSONResponse(status_code=exc.status_code, content={"mensaje": exc.detail})


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Maneja excepciones no controladas."""
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"mensaje": "Error interno del servidor", "detalles": str(exc)},
    )

"""Schemas de respuesta genéricos y utilitarios."""

from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel


class MensajeRespuesta(BaseModel):
    mensaje: str
    detalles: Optional[str] = None


class RespuestaPaginada(BaseModel):
    items: List[BaseModel]
    total: int
    pagina: int
    tamano_pagina: int
    total_paginas: int

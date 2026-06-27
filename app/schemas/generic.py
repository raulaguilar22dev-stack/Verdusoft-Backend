"""Schemas de respuesta genericos y utilitarios."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MensajeRespuesta(BaseModel):
    mensaje: str
    detalles: Optional[str] = None

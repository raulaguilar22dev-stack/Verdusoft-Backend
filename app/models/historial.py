"""Modelo de la tabla historial_precio."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HistorialPrecio(BaseModel):
    id_historial: int
    id_producto: int
    precio_anterior: Optional[float] = None
    precio_nuevo: float
    motivo: Optional[str] = None
    fecha_cambio: datetime

"""Schemas para el dominio Historial de Precios."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HistorialPrecioBase(BaseModel):
    id_producto: int = Field(..., gt=0)
    precio_anterior: Optional[float] = Field(None, ge=0)
    precio_nuevo: float = Field(..., ge=0)
    motivo: Optional[str] = Field(None, max_length=100)


class HistorialPrecioCreate(HistorialPrecioBase):
    pass


class HistorialPrecio(HistorialPrecioBase):
    id_historial: int
    fecha_cambio: datetime
    producto: Optional["Producto"] = None  # noqa: F821

    class Config:
        from_attributes = True

"""Schemas para reportes y estadisticas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ReporteStockBajo(BaseModel):
    id_producto: int
    nombre: str
    codigo: Optional[str] = None
    stock_actual: int
    stock_minimo: int
    diferencia: int

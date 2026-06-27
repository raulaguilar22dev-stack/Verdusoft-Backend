"""Modelo de la tabla producto."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.enums import UnidadMedidaEnum


class Producto(BaseModel):
    id_producto: int
    codigo: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    id_categoria: int
    precio_actual: float
    precio_costo: Optional[float] = None
    stock_minimo: int = 0
    stock: int = 0
    unidad_medida: UnidadMedidaEnum = UnidadMedidaEnum.UNIDAD
    activo: bool = True
    fecha_creacion: datetime
    fecha_actualizacion: datetime

"""Modelos de las tablas compra y detalle_compra."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.enums import EstadoEnum


class DetalleCompra(BaseModel):
    id_detalle_compra: int
    id_compra: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float


class Compra(BaseModel):
    id_compra: int
    numero_factura: Optional[str] = None
    id_proveedor: Optional[int] = None
    fecha: datetime
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADA
    total: float
    fecha_creacion: datetime
    detalles: List[DetalleCompra] = []

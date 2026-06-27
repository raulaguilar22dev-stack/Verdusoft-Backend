"""Modelos de las tablas venta y detalle_venta."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.enums import EstadoEnum, MetodoPagoEnum


class DetalleVenta(BaseModel):
    id_detalle_venta: int
    id_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    descuento: float = 0
    subtotal: float


class Venta(BaseModel):
    id_venta: int
    numero_ticket: Optional[str] = None
    id_cliente: Optional[int] = None
    fecha: datetime
    metodo_pago: MetodoPagoEnum = MetodoPagoEnum.EFECTIVO
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADA
    total: float
    fecha_creacion: datetime
    detalles: List[DetalleVenta] = []

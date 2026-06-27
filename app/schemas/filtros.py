"""Schemas para búsquedas y filtros."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.enums import MetodoPagoEnum, EstadoEnum


class FiltroProducto(BaseModel):
    nombre: Optional[str] = None
    id_categoria: Optional[int] = None
    codigo: Optional[str] = None
    stock_bajo: Optional[bool] = None
    activo: Optional[bool] = None
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None


class FiltroVenta(BaseModel):
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    id_cliente: Optional[int] = None
    metodo_pago: Optional[MetodoPagoEnum] = None
    estado: Optional[EstadoEnum] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None


class FiltroCompra(BaseModel):
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    id_proveedor: Optional[int] = None
    estado: Optional[EstadoEnum] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None

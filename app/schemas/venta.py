"""Schemas para el dominio Venta y DetalleVenta."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.schemas.enums import EstadoEnum, MetodoPagoEnum


class DetalleVentaBase(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., ge=0)
    descuento: float = Field(default=0, ge=0)


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVenta(DetalleVentaBase):
    id_detalle_venta: int
    id_venta: int
    subtotal: float
    producto: Optional["Producto"] = None  # noqa: F821

    class Config:
        from_attributes = True


class VentaBase(BaseModel):
    numero_ticket: Optional[str] = Field(None, max_length=50)
    id_cliente: Optional[int] = Field(None, gt=0)
    fecha: datetime = Field(default_factory=datetime.now)
    metodo_pago: MetodoPagoEnum = MetodoPagoEnum.EFECTIVO
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADA


class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate] = Field(..., min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_detalles(cls, v):
        if not v:
            raise ValueError("Debe incluir al menos un detalle de venta")
        return v


class VentaUpdate(BaseModel):
    numero_ticket: Optional[str] = Field(None, max_length=50)
    id_cliente: Optional[int] = Field(None, gt=0)
    metodo_pago: Optional[MetodoPagoEnum] = None
    observaciones: Optional[str] = None
    estado: Optional[EstadoEnum] = None


class Venta(VentaBase):
    id_venta: int
    total: float
    fecha_creacion: datetime
    cliente: Optional["Cliente"] = None  # noqa: F821
    detalles: List[DetalleVenta] = []

    class Config:
        from_attributes = True

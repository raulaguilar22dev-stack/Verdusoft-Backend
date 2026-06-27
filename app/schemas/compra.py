"""Schemas para el dominio Compra y DetalleCompra."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.schemas.enums import EstadoEnum


class DetalleCompraBase(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., ge=0)


class DetalleCompraCreate(DetalleCompraBase):
    pass


class DetalleCompra(DetalleCompraBase):
    id_detalle_compra: int
    id_compra: int
    subtotal: float
    producto: Optional["Producto"] = None  # noqa: F821

    class Config:
        from_attributes = True


class CompraBase(BaseModel):
    numero_factura: Optional[str] = Field(None, max_length=50)
    id_proveedor: Optional[int] = Field(None, gt=0)
    fecha: datetime = Field(default_factory=datetime.now)
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADA


class CompraCreate(CompraBase):
    detalles: List[DetalleCompraCreate] = Field(..., min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_detalles(cls, v):
        if not v:
            raise ValueError("Debe incluir al menos un detalle de compra")
        return v


class CompraUpdate(BaseModel):
    numero_factura: Optional[str] = Field(None, max_length=50)
    id_proveedor: Optional[int] = Field(None, gt=0)
    observaciones: Optional[str] = None
    estado: Optional[EstadoEnum] = None


class Compra(CompraBase):
    id_compra: int
    total: float
    fecha_creacion: datetime
    proveedor: Optional["Proveedor"] = None  # noqa: F821
    detalles: List[DetalleCompra] = []

    class Config:
        from_attributes = True

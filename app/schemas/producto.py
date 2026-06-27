"""Schemas para el dominio Producto."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.enums import UnidadMedidaEnum


class ProductoBase(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    id_categoria: int = Field(..., gt=0)
    precio_actual: float = Field(..., ge=0)
    precio_costo: Optional[float] = Field(None, ge=0)
    stock_minimo: int = Field(default=0, ge=0)
    stock: int = Field(default=0, ge=0)
    unidad_medida: UnidadMedidaEnum = UnidadMedidaEnum.UNIDAD
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    id_categoria: Optional[int] = Field(None, gt=0)
    precio_actual: Optional[float] = Field(None, ge=0)
    precio_costo: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    unidad_medida: Optional[UnidadMedidaEnum] = None
    activo: Optional[bool] = None


class Producto(ProductoBase):
    id_producto: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    categoria: Optional["Categoria"] = None  # noqa: F821

    class Config:
        from_attributes = True


class ProductoConStock(Producto):
    """Schema extendido con información de stock y alertas."""

    necesita_reposicion: bool = False

    @field_validator("necesita_reposicion", mode="before")
    @classmethod
    def calcular_necesita_reposicion(cls, v, info):
        stock = info.data.get("stock", 0)
        stock_minimo = info.data.get("stock_minimo", 0)
        return stock <= stock_minimo

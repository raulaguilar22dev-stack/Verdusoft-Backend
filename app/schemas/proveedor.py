"""Schemas para el dominio Proveedor."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ProveedorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class Proveedor(ProveedorBase):
    id_proveedor: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

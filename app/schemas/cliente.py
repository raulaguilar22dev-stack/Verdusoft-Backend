"""Schemas para el dominio Cliente."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class Cliente(ClienteBase):
    id_cliente: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

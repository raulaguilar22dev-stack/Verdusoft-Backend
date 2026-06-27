"""Modelo de la tabla cliente."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Cliente(BaseModel):
    id_cliente: int
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True
    fecha_creacion: datetime

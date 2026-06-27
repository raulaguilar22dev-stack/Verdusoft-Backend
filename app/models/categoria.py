"""Modelo de la tabla categoria."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Categoria(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    fecha_creacion: datetime

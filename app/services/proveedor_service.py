"""Servicio de lógica de negocio para Proveedores."""

from __future__ import annotations

import logging
from typing import Optional

from supabase import Client

from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate

logger = logging.getLogger(__name__)

TABLA = "proveedor"


def listar(
    db: Client,
    *,
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """Listar proveedores con paginación."""
    query = db.table(TABLA).select("*")
    if activo is not None:
        query = query.eq("activo", activo)
    query = query.order("nombre").range(skip, skip + limit - 1)
    response = query.execute()
    return response.data or []


def obtener(db: Client, id_proveedor: int) -> dict:
    """Obtener un proveedor por ID."""
    response = db.table(TABLA).select("*").eq("id_proveedor", id_proveedor).execute()
    if not response.data:
        raise ValueError("Proveedor no encontrado")
    return response.data[0]


def crear(db: Client, proveedor: ProveedorCreate) -> dict:
    """Crear un nuevo proveedor."""
    try:
        data = proveedor.model_dump(mode="json")
        response = db.table(TABLA).insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error al crear proveedor: {e}")
        raise ValueError("Error al crear proveedor")


def actualizar(db: Client, id_proveedor: int, proveedor: ProveedorUpdate) -> dict:
    """Actualizar un proveedor existente."""
    data = proveedor.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValueError("No hay datos para actualizar")
    response = db.table(TABLA).update(data).eq("id_proveedor", id_proveedor).execute()
    if not response.data:
        raise ValueError("Proveedor no encontrado")
    return response.data[0]


def eliminar(db: Client, id_proveedor: int) -> dict:
    """Desactivar (soft delete) un proveedor."""
    response = db.table(TABLA).update({"activo": False}).eq("id_proveedor", id_proveedor).execute()
    if not response.data:
        raise ValueError("Proveedor no encontrado")
    return {"mensaje": "Proveedor desactivado exitosamente"}

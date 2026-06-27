"""Servicio de lógica de negocio para Clientes."""

from __future__ import annotations

import logging
from typing import Optional

from supabase import Client

from app.schemas.cliente import ClienteCreate, ClienteUpdate

logger = logging.getLogger(__name__)

TABLA = "cliente"


def listar(
    db: Client,
    *,
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """Listar clientes con paginación."""
    query = db.table(TABLA).select("*")
    if activo is not None:
        query = query.eq("activo", activo)
    query = query.order("nombre").range(skip, skip + limit - 1)
    response = query.execute()
    return response.data or []


def obtener(db: Client, id_cliente: int) -> dict:
    """Obtener un cliente por ID."""
    response = db.table(TABLA).select("*").eq("id_cliente", id_cliente).execute()
    if not response.data:
        raise ValueError("Cliente no encontrado")
    return response.data[0]


def crear(db: Client, cliente: ClienteCreate) -> dict:
    """Crear un nuevo cliente."""
    try:
        data = cliente.model_dump(mode="json")
        response = db.table(TABLA).insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error al crear cliente: {e}")
        raise ValueError("Error al crear cliente")


def actualizar(db: Client, id_cliente: int, cliente: ClienteUpdate) -> dict:
    """Actualizar un cliente existente."""
    data = cliente.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValueError("No hay datos para actualizar")
    response = db.table(TABLA).update(data).eq("id_cliente", id_cliente).execute()
    if not response.data:
        raise ValueError("Cliente no encontrado")
    return response.data[0]


def eliminar(db: Client, id_cliente: int) -> dict:
    """Desactivar (soft delete) un cliente."""
    response = db.table(TABLA).update({"activo": False}).eq("id_cliente", id_cliente).execute()
    if not response.data:
        raise ValueError("Cliente no encontrado")
    return {"mensaje": "Cliente desactivado exitosamente"}

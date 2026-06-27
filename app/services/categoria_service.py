"""Servicio de lógica de negocio para Categorías."""

from __future__ import annotations

import logging
from typing import Optional

from postgrest.exceptions import APIError
from supabase import Client

from app.schemas.categoria import CategoriaCreate, CategoriaUpdate

logger = logging.getLogger(__name__)

TABLA = "categoria"


def listar(
    db: Client,
    *,
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """Listar categorías con paginación."""
    query = db.table(TABLA).select("*")
    if activo is not None:
        query = query.eq("activo", activo)
    query = query.order("nombre").range(skip, skip + limit - 1)
    response = query.execute()
    return response.data or []


def obtener(db: Client, id_categoria: int) -> dict:
    """Obtener una categoría por ID."""
    response = db.table(TABLA).select("*").eq("id_categoria", id_categoria).execute()
    if not response.data:
        raise ValueError("Categoría no encontrada")
    return response.data[0]


def crear(db: Client, categoria: CategoriaCreate) -> dict:
    """Crear una nueva categoría."""
    try:
        data = categoria.model_dump(mode="json")
        response = db.table(TABLA).insert(data).execute()
        return response.data[0]
    except APIError as e:
        logger.error(f"Error al crear categoría: {e}")
        if "duplicate" in str(e).lower():
            raise ValueError("Ya existe una categoría con ese nombre")
        raise ValueError("Error al crear categoría")


def actualizar(db: Client, id_categoria: int, categoria: CategoriaUpdate) -> dict:
    """Actualizar una categoría existente."""
    data = categoria.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValueError("No hay datos para actualizar")
    response = db.table(TABLA).update(data).eq("id_categoria", id_categoria).execute()
    if not response.data:
        raise ValueError("Categoría no encontrada")
    return response.data[0]


def eliminar(db: Client, id_categoria: int) -> dict:
    """Desactivar (soft delete) una categoría."""
    response = db.table(TABLA).update({"activo": False}).eq("id_categoria", id_categoria).execute()
    if not response.data:
        raise ValueError("Categoría no encontrada")
    return {"mensaje": "Categoría desactivada exitosamente"}

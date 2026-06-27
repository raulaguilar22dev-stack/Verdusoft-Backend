"""Servicio de logica de negocio para Productos."""

from __future__ import annotations

import logging
from typing import Optional

from postgrest.exceptions import APIError
from supabase import Client

from app.schemas.producto import ProductoCreate, ProductoUpdate

logger = logging.getLogger(__name__)

TABLA = "producto"


def listar(
    db: Client,
    *,
    nombre: Optional[str] = None,
    id_categoria: Optional[int] = None,
    codigo: Optional[str] = None,
    activo: Optional[bool] = None,
    stock_bajo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """Listar productos con filtros."""
    query = db.table(TABLA).select("*, categoria(*)")
    if nombre:
        query = query.ilike("nombre", f"%{nombre}%")
    if id_categoria:
        query = query.eq("id_categoria", id_categoria)
    if codigo:
        query = query.eq("codigo", codigo)
    if activo is not None:
        query = query.eq("activo", activo)
    if stock_bajo:
        # Filtro via VIEW en base de datos
        response = db.table("vw_stock_bajo").select("*").execute()
        return response.data or []

    query = query.order("nombre").range(skip, skip + limit - 1)
    response = query.execute()
    return response.data or []


def catalogo(db: Client) -> list[dict]:
    """Listado publico: solo activos con nombre y precio."""
    response = (
        db.table(TABLA)
        .select("id_producto, nombre, precio_actual")
        .eq("activo", True)
        .order("nombre")
        .execute()
    )
    return response.data or []


def stock_bajo(db: Client) -> list[dict]:
    """Obtener productos con stock bajo via VIEW."""
    response = db.table("vw_stock_bajo").select("*").execute()
    return response.data or []


def obtener(db: Client, id_producto: int) -> dict:
    """Obtener un producto por ID."""
    response = (
        db.table(TABLA).select("*, categoria(*)").eq("id_producto", id_producto).execute()
    )
    if not response.data:
        raise ValueError("Producto no encontrado")
    return response.data[0]


def crear(db: Client, producto: ProductoCreate) -> dict:
    """Crear un nuevo producto."""
    try:
        data = producto.model_dump(mode="json")
        response = db.table(TABLA).insert(data).execute()
        return response.data[0]
    except APIError as e:
        logger.error(f"Error al crear producto: {e}")
        if "duplicate" in str(e).lower():
            raise ValueError("Ya existe un producto con ese codigo")
        raise ValueError("Error al crear producto")


def actualizar(db: Client, id_producto: int, producto: ProductoUpdate) -> dict:
    """Actualizar un producto existente."""
    data = producto.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValueError("No hay datos para actualizar")
    response = db.table(TABLA).update(data).eq("id_producto", id_producto).execute()
    if not response.data:
        raise ValueError("Producto no encontrado")
    return response.data[0]


def eliminar(db: Client, id_producto: int) -> dict:
    """Desactivar (soft delete) un producto."""
    response = db.table(TABLA).update({"activo": False}).eq("id_producto", id_producto).execute()
    if not response.data:
        raise ValueError("Producto no encontrado")
    return {"mensaje": "Producto desactivado exitosamente"}

"""Servicio de logica de negocio para Compras."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from supabase import Client

from app.schemas.compra import CompraCreate, CompraUpdate

logger = logging.getLogger(__name__)

TABLA = "compra"
DETALLE_TABLA = "detalle_compra"


def listar(
    db: Client,
    *,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    id_proveedor: Optional[int] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """Listar compras con filtros."""
    query = db.table(TABLA).select("*, proveedor(*)")
    if fecha_inicio:
        query = query.gte("fecha", fecha_inicio.isoformat())
    if fecha_fin:
        query = query.lte("fecha", fecha_fin.isoformat())
    if id_proveedor:
        query = query.eq("id_proveedor", id_proveedor)
    if estado:
        query = query.eq("estado", estado)

    query = query.order("fecha", desc=True).range(skip, skip + limit - 1)
    response = query.execute()
    return response.data or []


def obtener(db: Client, id_compra: int) -> dict:
    """Obtener una compra por ID con sus detalles."""
    compra_response = db.table(TABLA).select("*, proveedor(*)").eq("id_compra", id_compra).execute()
    if not compra_response.data:
        raise ValueError("Compra no encontrada")

    compra = compra_response.data[0]
    detalles_response = (
        db.table(DETALLE_TABLA)
        .select("*, producto(*)")
        .eq("id_compra", id_compra)
        .execute()
    )
    compra["detalles"] = detalles_response.data or []
    return compra


def crear(db: Client, compra: CompraCreate) -> dict:
    """Crear una nueva compra con sus detalles (via RPC atomico)."""
    detalles_json = json.dumps([d.model_dump(mode="json") for d in compra.detalles])

    result = db.rpc(
        "crear_compra",
        {
            "p_numero_factura": compra.numero_factura,
            "p_id_proveedor": compra.id_proveedor,
            "p_fecha": compra.fecha.isoformat() if compra.fecha else None,
            "p_observaciones": compra.observaciones,
            "p_estado": compra.estado.value if compra.estado else None,
            "p_detalles": detalles_json,
        },
    ).execute()

    if not result.data:
        raise ValueError("Error al crear compra via RPC")

    id_compra = result.data[0].get("id_compra")
    if not id_compra:
        raise ValueError("Respuesta inesperada del RPC crear_compra")

    return obtener(db, id_compra)


def actualizar(db: Client, id_compra: int, compra: CompraUpdate) -> dict:
    """Actualizar una compra (solo encabezado)."""
    data = compra.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValueError("No hay datos para actualizar")
    response = db.table(TABLA).update(data).eq("id_compra", id_compra).execute()
    if not response.data:
        raise ValueError("Compra no encontrada")
    return obtener(db, id_compra)


def cancelar(db: Client, id_compra: int) -> dict:
    """Cancelar una compra (revertir stock)."""
    result = db.rpc("cancelar_compra", {"p_id_compra": id_compra}).execute()
    if not result.data:
        raise ValueError("Error al cancelar compra via RPC")
    return {"mensaje": "Compra cancelada exitosamente"}

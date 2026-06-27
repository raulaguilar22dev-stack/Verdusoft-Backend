"""Servicio de logica de negocio para Ventas."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from supabase import Client

from app.schemas.venta import VentaCreate, VentaUpdate

logger = logging.getLogger(__name__)

TABLA = "venta"
DETALLE_TABLA = "detalle_venta"
TABLA_PRODUCTO = "producto"


def listar(
    db: Client,
    *,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    id_cliente: Optional[int] = None,
    metodo_pago: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """Listar ventas con filtros."""
    query = db.table(TABLA).select("*, cliente(*)")
    if fecha_inicio:
        query = query.gte("fecha", fecha_inicio.isoformat())
    if fecha_fin:
        query = query.lte("fecha", fecha_fin.isoformat())
    if id_cliente:
        query = query.eq("id_cliente", id_cliente)
    if metodo_pago:
        query = query.eq("metodo_pago", metodo_pago)
    if estado:
        query = query.eq("estado", estado)

    query = query.order("fecha", desc=True).range(skip, skip + limit - 1)
    response = query.execute()
    return response.data or []


def obtener(db: Client, id_venta: int) -> dict:
    """Obtener una venta por ID con sus detalles."""
    venta_response = db.table(TABLA).select("*, cliente(*)").eq("id_venta", id_venta).execute()
    if not venta_response.data:
        raise ValueError("Venta no encontrada")

    venta = venta_response.data[0]
    detalles_response = (
        db.table(DETALLE_TABLA)
        .select("*, producto(*)")
        .eq("id_venta", id_venta)
        .execute()
    )
    venta["detalles"] = detalles_response.data or []
    return venta


def crear(db: Client, venta: VentaCreate) -> dict:
    """Crear una nueva venta con sus detalles (via RPC atomico)."""
    detalles_json = json.dumps([d.model_dump(mode="json") for d in venta.detalles])

    result = db.rpc(
        "crear_venta",
        {
            "p_numero_ticket": venta.numero_ticket,
            "p_id_cliente": venta.id_cliente,
            "p_fecha": venta.fecha.isoformat() if venta.fecha else None,
            "p_metodo_pago": venta.metodo_pago.value if venta.metodo_pago else None,
            "p_observaciones": venta.observaciones,
            "p_estado": venta.estado.value if venta.estado else None,
            "p_detalles": detalles_json,
        },
    ).execute()

    if not result.data:
        raise ValueError("Error al crear venta via RPC")

    id_venta = result.data[0].get("id_venta")
    if not id_venta:
        raise ValueError("Respuesta inesperada del RPC crear_venta")

    return obtener(db, id_venta)


def actualizar(db: Client, id_venta: int, venta: VentaUpdate) -> dict:
    """Actualizar una venta (solo encabezado)."""
    data = venta.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValueError("No hay datos para actualizar")
    response = db.table(TABLA).update(data).eq("id_venta", id_venta).execute()
    if not response.data:
        raise ValueError("Venta no encontrada")
    return obtener(db, id_venta)


def cancelar(db: Client, id_venta: int) -> dict:
    """Cancelar una venta (revertir stock)."""
    result = db.rpc("cancelar_venta", {"p_id_venta": id_venta}).execute()
    if not result.data:
        raise ValueError("Error al cancelar venta via RPC")
    return {"mensaje": "Venta cancelada exitosamente"}

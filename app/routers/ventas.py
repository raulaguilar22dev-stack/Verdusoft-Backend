"""Router de endpoints para Ventas."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_supabase_client
from app.schemas import MensajeRespuesta, Venta, VentaCreate, VentaUpdate
from app.services import venta_service

router = APIRouter(prefix="/api", tags=["Ventas"])


@router.get("/ventas", response_model=List[Venta])
def listar_ventas(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    id_cliente: Optional[int] = None,
    metodo_pago: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_supabase_client),
):
    """Listar todas las ventas con filtros."""
    try:
        return venta_service.listar(
            db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_cliente=id_cliente,
            metodo_pago=metodo_pago,
            estado=estado,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener ventas")


@router.get("/ventas/{id_venta}", response_model=Venta)
def obtener_venta(id_venta: int, db=Depends(get_supabase_client)):
    """Obtener una venta por ID con sus detalles."""
    try:
        return venta_service.obtener(db, id_venta)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener venta")


@router.post(
    "/ventas",
    response_model=Venta,
    status_code=status.HTTP_201_CREATED,
)
def crear_venta(venta: VentaCreate, db=Depends(get_supabase_client)):
    """Crear una nueva venta con sus detalles."""
    try:
        return venta_service.crear(db, venta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear venta: {e}")


@router.patch("/ventas/{id_venta}", response_model=Venta)
def actualizar_venta(
    id_venta: int,
    venta: VentaUpdate,
    db=Depends(get_supabase_client),
):
    """Actualizar una venta (solo encabezado)."""
    try:
        return venta_service.actualizar(db, id_venta, venta)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar venta")


@router.delete("/ventas/{id_venta}", response_model=MensajeRespuesta)
def cancelar_venta(id_venta: int, db=Depends(get_supabase_client)):
    """Cancelar una venta."""
    try:
        return venta_service.cancelar(db, id_venta)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cancelar venta")

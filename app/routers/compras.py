"""Router de endpoints para Compras."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_supabase_client
from app.schemas import Compra, CompraCreate, CompraUpdate, MensajeRespuesta
from app.services import compra_service

router = APIRouter(prefix="/api", tags=["Compras"])


@router.get("/compras", response_model=List[Compra])
def listar_compras(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    id_proveedor: Optional[int] = None,
    estado: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_supabase_client),
):
    """Listar todas las compras con filtros."""
    try:
        return compra_service.listar(
            db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_proveedor=id_proveedor,
            estado=estado,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener compras")


@router.get("/compras/{id_compra}", response_model=Compra)
def obtener_compra(id_compra: int, db=Depends(get_supabase_client)):
    """Obtener una compra por ID con sus detalles."""
    try:
        return compra_service.obtener(db, id_compra)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener compra")


@router.post(
    "/compras",
    response_model=Compra,
    status_code=status.HTTP_201_CREATED,
)
def crear_compra(compra: CompraCreate, db=Depends(get_supabase_client)):
    """Crear una nueva compra con sus detalles."""
    try:
        return compra_service.crear(db, compra)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear compra: {e}")


@router.patch("/compras/{id_compra}", response_model=Compra)
def actualizar_compra(
    id_compra: int,
    compra: CompraUpdate,
    db=Depends(get_supabase_client),
):
    """Actualizar una compra (solo encabezado)."""
    try:
        return compra_service.actualizar(db, id_compra, compra)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar compra")


@router.delete("/compras/{id_compra}", response_model=MensajeRespuesta)
def cancelar_compra(id_compra: int, db=Depends(get_supabase_client)):
    """Cancelar una compra."""
    try:
        return compra_service.cancelar(db, id_compra)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al cancelar compra")

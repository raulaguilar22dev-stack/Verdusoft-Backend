"""Router de endpoints para Clientes."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_supabase_client
from app.schemas import Cliente, ClienteCreate, ClienteUpdate, MensajeRespuesta
from app.services import cliente_service

router = APIRouter(prefix="/api", tags=["Clientes"])


@router.get("/clientes", response_model=List[Cliente])
def listar_clientes(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_supabase_client),
):
    """Listar todos los clientes."""
    try:
        return cliente_service.listar(db, activo=activo, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener clientes")


@router.get("/clientes/{id_cliente}", response_model=Cliente)
def obtener_cliente(id_cliente: int, db=Depends(get_supabase_client)):
    """Obtener un cliente por ID."""
    try:
        return cliente_service.obtener(db, id_cliente)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener cliente")


@router.post(
    "/clientes",
    response_model=Cliente,
    status_code=status.HTTP_201_CREATED,
)
def crear_cliente(cliente: ClienteCreate, db=Depends(get_supabase_client)):
    """Crear un nuevo cliente."""
    try:
        return cliente_service.crear(db, cliente)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/clientes/{id_cliente}", response_model=Cliente)
def actualizar_cliente(
    id_cliente: int,
    cliente: ClienteUpdate,
    db=Depends(get_supabase_client),
):
    """Actualizar un cliente."""
    try:
        return cliente_service.actualizar(db, id_cliente, cliente)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar cliente")


@router.delete("/clientes/{id_cliente}", response_model=MensajeRespuesta)
def eliminar_cliente(id_cliente: int, db=Depends(get_supabase_client)):
    """Desactivar un cliente."""
    try:
        return cliente_service.eliminar(db, id_cliente)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar cliente")

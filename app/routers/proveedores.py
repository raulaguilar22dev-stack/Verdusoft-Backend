"""Router de endpoints para Proveedores."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import require_admin
from app.dependencies import get_supabase_client
from app.schemas import MensajeRespuesta, Proveedor, ProveedorCreate, ProveedorUpdate
from app.services import proveedor_service

router = APIRouter(
    prefix="/api",
    tags=["Proveedores"],
    dependencies=[Depends(require_admin)],
)


@router.get("/proveedores", response_model=List[Proveedor])
def listar_proveedores(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_supabase_client),
):
    """Listar todos los proveedores."""
    try:
        return proveedor_service.listar(db, activo=activo, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener proveedores")


@router.get("/proveedores/{id_proveedor}", response_model=Proveedor)
def obtener_proveedor(id_proveedor: int, db=Depends(get_supabase_client)):
    """Obtener un proveedor por ID."""
    try:
        return proveedor_service.obtener(db, id_proveedor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener proveedor")


@router.post(
    "/proveedores",
    response_model=Proveedor,
    status_code=status.HTTP_201_CREATED,
)
def crear_proveedor(proveedor: ProveedorCreate, db=Depends(get_supabase_client)):
    """Crear un nuevo proveedor."""
    try:
        return proveedor_service.crear(db, proveedor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/proveedores/{id_proveedor}", response_model=Proveedor)
def actualizar_proveedor(
    id_proveedor: int,
    proveedor: ProveedorUpdate,
    db=Depends(get_supabase_client),
):
    """Actualizar un proveedor."""
    try:
        return proveedor_service.actualizar(db, id_proveedor, proveedor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar proveedor")


@router.delete("/proveedores/{id_proveedor}", response_model=MensajeRespuesta)
def eliminar_proveedor(id_proveedor: int, db=Depends(get_supabase_client)):
    """Desactivar un proveedor."""
    try:
        return proveedor_service.eliminar(db, id_proveedor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar proveedor")

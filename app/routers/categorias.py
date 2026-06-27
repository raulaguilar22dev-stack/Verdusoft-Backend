"""Router de endpoints para Categorías."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_supabase_client
from app.schemas import Categoria, CategoriaCreate, CategoriaUpdate, MensajeRespuesta
from app.services import categoria_service

router = APIRouter(prefix="/api", tags=["Categorías"])


@router.get("/categorias", response_model=List[Categoria])
def listar_categorias(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_supabase_client),
):
    """Listar todas las categorías con paginación."""
    try:
        return categoria_service.listar(db, activo=activo, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener categorías")


@router.get("/categorias/{id_categoria}", response_model=Categoria)
def obtener_categoria(id_categoria: int, db=Depends(get_supabase_client)):
    """Obtener una categoría por ID."""
    try:
        return categoria_service.obtener(db, id_categoria)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener categoría")


@router.post(
    "/categorias",
    response_model=Categoria,
    status_code=status.HTTP_201_CREATED,
)
def crear_categoria(categoria: CategoriaCreate, db=Depends(get_supabase_client)):
    """Crear una nueva categoría."""
    try:
        return categoria_service.crear(db, categoria)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/categorias/{id_categoria}", response_model=Categoria)
def actualizar_categoria(
    id_categoria: int,
    categoria: CategoriaUpdate,
    db=Depends(get_supabase_client),
):
    """Actualizar una categoría existente."""
    try:
        return categoria_service.actualizar(db, id_categoria, categoria)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar categoría")


@router.delete("/categorias/{id_categoria}", response_model=MensajeRespuesta)
def eliminar_categoria(id_categoria: int, db=Depends(get_supabase_client)):
    """Eliminar (desactivar) una categoría."""
    try:
        return categoria_service.eliminar(db, id_categoria)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar categoría")

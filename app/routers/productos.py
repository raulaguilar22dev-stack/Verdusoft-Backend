"""Router de endpoints para Productos."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_supabase_client
from app.schemas import MensajeRespuesta, Producto, ProductoCreate, ProductoUpdate, ProductoPublic, ReporteStockBajo
from app.services import producto_service

router = APIRouter(prefix="/api", tags=["Productos"])


@router.get("/productos", response_model=List[Producto])
def listar_productos(
    nombre: Optional[str] = None,
    id_categoria: Optional[int] = None,
    codigo: Optional[str] = None,
    activo: Optional[bool] = None,
    stock_bajo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db=Depends(get_supabase_client),
):
    """Listar todos los productos con filtros."""
    try:
        return producto_service.listar(
            db,
            nombre=nombre,
            id_categoria=id_categoria,
            codigo=codigo,
            activo=activo,
            stock_bajo=stock_bajo,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener productos")


@router.get("/productos/catalogo", response_model=List[ProductoPublic])
def catalogo_productos(db=Depends(get_supabase_client)):
    """Listado publico de productos (solo nombre y precio)."""
    try:
        return producto_service.catalogo(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener catalogo")


@router.get("/productos/stock-bajo", response_model=List[ReporteStockBajo])
def productos_stock_bajo(db=Depends(get_supabase_client)):
    """Obtener productos con stock bajo."""
    try:
        return producto_service.stock_bajo(db)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error al obtener productos con stock bajo"
        )


@router.get("/productos/{id_producto}", response_model=Producto)
def obtener_producto(id_producto: int, db=Depends(get_supabase_client)):
    """Obtener un producto por ID."""
    try:
        return producto_service.obtener(db, id_producto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener producto")


@router.post(
    "/productos",
    response_model=Producto,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(producto: ProductoCreate, db=Depends(get_supabase_client)):
    """Crear un nuevo producto."""
    try:
        return producto_service.crear(db, producto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/productos/{id_producto}", response_model=Producto)
def actualizar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    db=Depends(get_supabase_client),
):
    """Actualizar un producto."""
    try:
        return producto_service.actualizar(db, id_producto, producto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar producto")


@router.delete("/productos/{id_producto}", response_model=MensajeRespuesta)
def eliminar_producto(id_producto: int, db=Depends(get_supabase_client)):
    """Desactivar un producto."""
    try:
        return producto_service.eliminar(db, id_producto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar producto")

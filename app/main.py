"""Entry point de la aplicación FastAPI."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.exceptions import general_exception_handler, http_exception_handler
from app.routers import categorias, clientes, compras, productos, proveedores, ventas

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Sistema de Inventario API",
    description="API para gestión de inventario, compras y ventas con Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(categorias.router)
app.include_router(proveedores.router)
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(compras.router)
app.include_router(ventas.router)


@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al Sistema de Inventario API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    from app.database import get_supabase

    try:
        db = get_supabase()
        db.table("categoria").select("id_categoria").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail=f"Database error: {e}")

"""Entry point de la aplicación FastAPI."""

import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.auth.dependencies import require_admin
from app.exceptions import general_exception_handler, http_exception_handler
from app.routers import auth, categorias, clientes, compras, productos, proveedores, ventas

logging.basicConfig(level=logging.INFO)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Sistema de Inventario API",
    description="API para gestión de inventario, compras y ventas con Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://verdusoft-front.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Auth (publico: registro con master key)
app.include_router(auth.router)

# Productos: catalogo publico, el resto admin
app.include_router(productos.router)

# Admin only
app.include_router(
    categorias.router, dependencies=[Depends(require_admin)]
)
app.include_router(
    proveedores.router, dependencies=[Depends(require_admin)]
)
app.include_router(
    clientes.router, dependencies=[Depends(require_admin)]
)
app.include_router(
    compras.router, dependencies=[Depends(require_admin)]
)
app.include_router(
    ventas.router, dependencies=[Depends(require_admin)]
)


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

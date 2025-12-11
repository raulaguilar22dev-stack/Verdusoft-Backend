import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from supabase import create_client, Client
from postgrest.exceptions import APIError
import logging


#########################################################prueba de respuesta################################################
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
#################################################################################################################

from schemas import (
    # Categoria
    Categoria,
    CategoriaCreate,
    CategoriaUpdate,
    # Proveedor
    Proveedor,
    ProveedorCreate,
    ProveedorUpdate,
    # Cliente
    Cliente,
    ClienteCreate,
    ClienteUpdate,
    # Producto
    Producto,
    ProductoCreate,
    ProductoUpdate,
    ProductoConStock,
    # Compra
    Compra,
    CompraCreate,
    CompraUpdate,
    DetalleCompra,
    # Venta
    Venta,
    VentaCreate,
    VentaUpdate,
    DetalleVenta,
    # Historial
    HistorialPrecio,
    # Reportes
    ReporteStockBajo,
    ReporteVentasPeriodo,
    # Genéricos
    MensajeRespuesta,
)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Inventario API",
    description="API para gestión de inventario, compras y ventas con Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

##################################################prueba################################################
app.mount("/static", StaticFiles(directory="static"), name="static")
#######################################################################################################

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================
# EXCEPTION HANDLERS
# ==============================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"mensaje": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"mensaje": "Error interno del servidor", "detalles": str(exc)},
    )


# ==============================================
# ROOT ENDPOINTS
# ==============================================


@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al Sistema de Inventario API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    try:
        # Verificar conexión a Supabase
        supabase.table("categoria").select("id_categoria").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


# ==============================================
# ENDPOINTS: CATEGORIAS
# ==============================================


@app.get("/api/categorias", response_model=List[Categoria], tags=["Categorías"])
def listar_categorias(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar todas las categorías con paginación"""
    try:
        query = supabase.table("categoria").select("*")

        if activo is not None:
            query = query.eq("activo", activo)

        query = query.order("nombre").range(skip, skip + limit - 1)
        response = query.execute()

        return response.data
    except APIError as e:
        logger.error(f"Error al listar categorías: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener categorías")


@app.get(
    "/api/categorias/{id_categoria}", response_model=Categoria, tags=["Categorías"]
)
def obtener_categoria(id_categoria: int):
    """Obtener una categoría por ID"""
    try:
        response = (
            supabase.table("categoria")
            .select("*")
            .eq("id_categoria", id_categoria)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener categoría: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener categoría")


@app.post(
    "/api/categorias",
    response_model=Categoria,
    status_code=status.HTTP_201_CREATED,
    tags=["Categorías"],
)
def crear_categoria(categoria: CategoriaCreate):
    """Crear una nueva categoría"""
    try:
        data = categoria.model_dump(mode="json")
        response = supabase.table("categoria").insert(data).execute()
        return response.data[0]
    except APIError as e:
        logger.error(f"Error al crear categoría: {str(e)}")
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=400, detail="Ya existe una categoría con ese nombre"
            )
        raise HTTPException(status_code=400, detail="Error al crear categoría")


@app.patch(
    "/api/categorias/{id_categoria}", response_model=Categoria, tags=["Categorías"]
)
def actualizar_categoria(id_categoria: int, categoria: CategoriaUpdate):
    """Actualizar una categoría existente"""
    try:
        data = categoria.model_dump(exclude_unset=True, mode="json")
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        response = (
            supabase.table("categoria")
            .update(data)
            .eq("id_categoria", id_categoria)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar categoría: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar categoría")


@app.delete(
    "/api/categorias/{id_categoria}",
    response_model=MensajeRespuesta,
    tags=["Categorías"],
)
def eliminar_categoria(id_categoria: int):
    """Eliminar (desactivar) una categoría"""
    try:
        # Soft delete - solo desactivar
        response = (
            supabase.table("categoria")
            .update({"activo": False})
            .eq("id_categoria", id_categoria)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return MensajeRespuesta(mensaje="Categoría desactivada exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar categoría: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar categoría")


# ==============================================
# ENDPOINTS: PROVEEDORES
# ==============================================


@app.get("/api/proveedores", response_model=List[Proveedor], tags=["Proveedores"])
def listar_proveedores(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar todos los proveedores"""
    try:
        query = supabase.table("proveedor").select("*")

        if activo is not None:
            query = query.eq("activo", activo)

        query = query.order("nombre").range(skip, skip + limit - 1)
        response = query.execute()

        return response.data
    except Exception as e:
        logger.error(f"Error al listar proveedores: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener proveedores")


@app.get(
    "/api/proveedores/{id_proveedor}", response_model=Proveedor, tags=["Proveedores"]
)
def obtener_proveedor(id_proveedor: int):
    """Obtener un proveedor por ID"""
    try:
        response = (
            supabase.table("proveedor")
            .select("*")
            .eq("id_proveedor", id_proveedor)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener proveedor: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener proveedor")


@app.post(
    "/api/proveedores",
    response_model=Proveedor,
    status_code=status.HTTP_201_CREATED,
    tags=["Proveedores"],
)
def crear_proveedor(proveedor: ProveedorCreate):
    """Crear un nuevo proveedor"""
    try:
        data = proveedor.model_dump(mode="json")
        response = supabase.table("proveedor").insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error al crear proveedor: {str(e)}")
        raise HTTPException(status_code=400, detail="Error al crear proveedor")


@app.patch(
    "/api/proveedores/{id_proveedor}", response_model=Proveedor, tags=["Proveedores"]
)
def actualizar_proveedor(id_proveedor: int, proveedor: ProveedorUpdate):
    """Actualizar un proveedor"""
    try:
        data = proveedor.model_dump(exclude_unset=True, mode="json")
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        response = (
            supabase.table("proveedor")
            .update(data)
            .eq("id_proveedor", id_proveedor)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar proveedor: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar proveedor")


@app.delete(
    "/api/proveedores/{id_proveedor}",
    response_model=MensajeRespuesta,
    tags=["Proveedores"],
)
def eliminar_proveedor(id_proveedor: int):
    """Desactivar un proveedor"""
    try:
        response = (
            supabase.table("proveedor")
            .update({"activo": False})
            .eq("id_proveedor", id_proveedor)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        return MensajeRespuesta(mensaje="Proveedor desactivado exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar proveedor: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar proveedor")


# ==============================================
# ENDPOINTS: CLIENTES
# ==============================================


@app.get("/api/clientes", response_model=List[Cliente], tags=["Clientes"])
def listar_clientes(
    activo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar todos los clientes"""
    try:
        query = supabase.table("cliente").select("*")

        if activo is not None:
            query = query.eq("activo", activo)

        query = query.order("nombre").range(skip, skip + limit - 1)
        response = query.execute()

        return response.data
    except Exception as e:
        logger.error(f"Error al listar clientes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener clientes")


@app.get("/api/clientes/{id_cliente}", response_model=Cliente, tags=["Clientes"])
def obtener_cliente(id_cliente: int):
    """Obtener un cliente por ID"""
    try:
        response = (
            supabase.table("cliente").select("*").eq("id_cliente", id_cliente).execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cliente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener cliente")


@app.post(
    "/api/clientes",
    response_model=Cliente,
    status_code=status.HTTP_201_CREATED,
    tags=["Clientes"],
)
def crear_cliente(cliente: ClienteCreate):
    """Crear un nuevo cliente"""
    try:
        data = cliente.model_dump(mode="json")
        response = supabase.table("cliente").insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error al crear cliente: {str(e)}")
        raise HTTPException(status_code=400, detail="Error al crear cliente")


@app.patch("/api/clientes/{id_cliente}", response_model=Cliente, tags=["Clientes"])
def actualizar_cliente(id_cliente: int, cliente: ClienteUpdate):
    """Actualizar un cliente"""
    try:
        data = cliente.model_dump(exclude_unset=True, mode="json")
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        response = (
            supabase.table("cliente")
            .update(data)
            .eq("id_cliente", id_cliente)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar cliente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar cliente")


@app.delete(
    "/api/clientes/{id_cliente}", response_model=MensajeRespuesta, tags=["Clientes"]
)
def eliminar_cliente(id_cliente: int):
    """Desactivar un cliente"""
    try:
        response = (
            supabase.table("cliente")
            .update({"activo": False})
            .eq("id_cliente", id_cliente)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return MensajeRespuesta(mensaje="Cliente desactivado exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar cliente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar cliente")


# ==============================================
# ENDPOINTS: PRODUCTOS
# ==============================================


@app.get("/api/productos", response_model=List[Producto], tags=["Productos"])
def listar_productos(
    nombre: Optional[str] = None,
    id_categoria: Optional[int] = None,
    codigo: Optional[str] = None,
    activo: Optional[bool] = None,
    stock_bajo: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar todos los productos con filtros"""
    try:
        query = supabase.table("producto").select("*, categoria(*)")

        if nombre:
            query = query.ilike("nombre", f"%{nombre}%")
        if id_categoria:
            query = query.eq("id_categoria", id_categoria)
        if codigo:
            query = query.eq("codigo", codigo)
        if activo is not None:
            query = query.eq("activo", activo)

        query = query.order("nombre").range(skip, skip + limit - 1)
        response = query.execute()

        productos = response.data

        # Filtrar productos con stock bajo si se solicita
        if stock_bajo:
            productos = [
                p for p in productos if p.get("stock", 0) <= p.get("stock_minimo", 0)
            ]

        return productos
    except Exception as e:
        logger.error(f"Error al listar productos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener productos")


@app.get(
    "/api/productos/stock-bajo",
    response_model=List[ReporteStockBajo],
    tags=["Productos"],
)
def productos_stock_bajo():
    """Obtener productos con stock bajo"""
    try:
        # Usar RPC para consulta personalizada o filtrar en Python
        response = (
            supabase.table("producto")
            .select("id_producto, nombre, codigo, stock, stock_minimo")
            .eq("activo", True)
            .execute()
        )

        productos_bajo_stock = []
        for p in response.data:
            if p["stock"] <= p["stock_minimo"]:
                productos_bajo_stock.append(
                    {
                        "id_producto": p["id_producto"],
                        "nombre": p["nombre"],
                        "codigo": p.get("codigo"),
                        "stock_actual": p["stock"],
                        "stock_minimo": p["stock_minimo"],
                        "diferencia": p["stock_minimo"] - p["stock"],
                    }
                )

        return productos_bajo_stock
    except Exception as e:
        logger.error(f"Error al obtener productos con stock bajo: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al obtener productos con stock bajo"
        )


@app.get("/api/productos/{id_producto}", response_model=Producto, tags=["Productos"])
def obtener_producto(id_producto: int):
    """Obtener un producto por ID"""
    try:
        response = (
            supabase.table("producto")
            .select("*, categoria(*)")
            .eq("id_producto", id_producto)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener producto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener producto")


@app.post(
    "/api/productos",
    response_model=Producto,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
)
def crear_producto(producto: ProductoCreate):
    """Crear un nuevo producto"""
    try:
        data = producto.model_dump(mode="json")
        response = supabase.table("producto").insert(data).execute()
        return response.data[0]
    except APIError as e:
        logger.error(f"Error al crear producto: {str(e)}")
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=400, detail="Ya existe un producto con ese código"
            )
        raise HTTPException(status_code=400, detail="Error al crear producto")


@app.patch("/api/productos/{id_producto}", response_model=Producto, tags=["Productos"])
def actualizar_producto(id_producto: int, producto: ProductoUpdate):
    """Actualizar un producto"""
    try:
        data = producto.model_dump(exclude_unset=True, mode="json")
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        response = (
            supabase.table("producto")
            .update(data)
            .eq("id_producto", id_producto)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar producto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar producto")


@app.delete(
    "/api/productos/{id_producto}", response_model=MensajeRespuesta, tags=["Productos"]
)
def eliminar_producto(id_producto: int):
    """Desactivar un producto"""
    try:
        response = (
            supabase.table("producto")
            .update({"activo": False})
            .eq("id_producto", id_producto)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return MensajeRespuesta(mensaje="Producto desactivado exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar producto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar producto")


# ==============================================
# ENDPOINTS: COMPRAS
# ==============================================


@app.get("/api/compras", response_model=List[Compra], tags=["Compras"])
def listar_compras(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    id_proveedor: Optional[int] = None,
    estado: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar todas las compras con filtros"""
    try:
        query = supabase.table("compra").select("*, proveedor(*)")

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

        return response.data
    except Exception as e:
        logger.error(f"Error al listar compras: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener compras")


@app.get("/api/compras/{id_compra}", response_model=Compra, tags=["Compras"])
def obtener_compra(id_compra: int):
    """Obtener una compra por ID con sus detalles"""
    try:
        # Obtener compra
        compra_response = (
            supabase.table("compra")
            .select("*, proveedor(*)")
            .eq("id_compra", id_compra)
            .execute()
        )

        if not compra_response.data:
            raise HTTPException(status_code=404, detail="Compra no encontrada")

        compra = compra_response.data[0]

        # Obtener detalles
        detalles_response = (
            supabase.table("detalle_compra")
            .select("*, producto(*)")
            .eq("id_compra", id_compra)
            .execute()
        )
        compra["detalles"] = detalles_response.data

        return compra
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener compra: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener compra")


@app.post(
    "/api/compras",
    response_model=Compra,
    status_code=status.HTTP_201_CREATED,
    tags=["Compras"],
)
def crear_compra(compra: CompraCreate):
    """Crear una nueva compra con sus detalles"""
    try:
        # Insertar compra
        compra_data = compra.model_dump(exclude={"detalles"}, mode="json")
        compra_response = supabase.table("compra").insert(compra_data).execute()

        if not compra_response.data:
            raise HTTPException(status_code=400, detail="Error al crear compra")

        id_compra = compra_response.data[0]["id_compra"]

        # Insertar detalles
        detalles_data = []
        for detalle in compra.detalles:
            detalle_dict = detalle.model_dump(mode="json")
            detalle_dict["id_compra"] = id_compra
            detalles_data.append(detalle_dict)

        if detalles_data:
            supabase.table("detalle_compra").insert(detalles_data).execute()

        # Retornar compra completa
        return obtener_compra(id_compra)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear compra: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error al crear compra: {str(e)}")


@app.patch("/api/compras/{id_compra}", response_model=Compra, tags=["Compras"])
def actualizar_compra(id_compra: int, compra: CompraUpdate):
    """Actualizar una compra (solo encabezado)"""
    try:
        data = compra.model_dump(exclude_unset=True, mode="json")
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")

        response = (
            supabase.table("compra").update(data).eq("id_compra", id_compra).execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Compra no encontrada")

        return obtener_compra(id_compra)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar compra: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar compra")


@app.delete(
    "/api/compras/{id_compra}", response_model=MensajeRespuesta, tags=["Compras"]
)
def cancelar_compra(id_compra: int):
    """Cancelar una compra"""
    try:
        response = (
            supabase.table("compra")
            .update({"estado": "cancelada"})
            .eq("id_compra", id_compra)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Compra no encontrada")

        return MensajeRespuesta(mensaje="Compra cancelada exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar compra: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cancelar compra")


# ==============================================
# ENDPOINTS: VENTAS
# ==============================================


@app.get("/api/ventas", response_model=List[Venta], tags=["Ventas"])
def listar_ventas(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    id_cliente: Optional[int] = None,
    metodo_pago: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar todas las ventas con filtros"""
    try:
        query = supabase.table("venta").select("*, cliente(*)")

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

        return response.data
    except Exception as e:
        logger.error(f"Error al listar ventas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener ventas")


@app.get("/api/ventas/{id_venta}", response_model=Venta, tags=["Ventas"])
def obtener_venta(id_venta: int):
    """Obtener una venta por ID con sus detalles"""
    try:
        # Obtener venta
        venta_response = (
            supabase.table("venta")
            .select("*, cliente(*)")
            .eq("id_venta", id_venta)
            .execute()
        )

        if not venta_response.data:
            raise HTTPException(status_code=404, detail="Venta no encontrada")

        venta = venta_response.data[0]

        # Obtener detalles
        detalles_response = (
            supabase.table("detalle_venta")
            .select("*, producto(*)")
            .eq("id_venta", id_venta)
            .execute()
        )
        venta["detalles"] = detalles_response.data

        return venta
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener venta: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener venta")


@app.post(
    "/api/ventas",
    response_model=Venta,
    status_code=status.HTTP_201_CREATED,
    tags=["Ventas"],
)
def crear_venta(venta: VentaCreate):
    """Crear una nueva venta con sus detalles"""
    try:
        # Verificar stock disponible
        for detalle in venta.detalles:
            producto_response = (
                supabase.table("producto")
                .select("stock")
                .eq("id_producto", detalle.id_producto)
                .execute()
            )

            if not producto_response.data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {detalle.id_producto} no encontrado",
                )

            stock_actual = producto_response.data[0]["stock"]
            if stock_actual < detalle.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para producto {detalle.id_producto}. Stock actual: {stock_actual}",
                )

        # Insertar venta
        venta_data = venta.model_dump(exclude={"detalles"}, mode="json")
        venta_response = supabase.table("venta").insert(venta_data).execute()

        if not venta_response.data:
            raise HTTPException(status_code=400, detail="Error al crear venta")

        id_venta = venta_response.data[0]["id_venta"]

        # Insertar detalles
        detalles_data = []
        for detalle in venta.detalles:
            detalle_dict = detalle.model_dump(mode="json")
            detalle_dict["id_venta"] = id_venta
            detalles_data.append(detalle_dict)

        if detalles_data:
            supabase.table("detalle_venta").insert(detalles_data).execute()

        # Retornar venta completa
        return obtener_venta(id_venta)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear venta: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error al crear venta: {str(e)}")


@app.get("/tienda")
def read_index():
    return FileResponse("static/index.html")


@app.get("/ventas")
def read_ventas():
    return FileResponse("static/historial_ventas.html")

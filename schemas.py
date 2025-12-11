from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# ==============================================
# ENUMS
# ==============================================


class EstadoEnum(str, Enum):
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    PENDIENTE = "pendiente"


class MetodoPagoEnum(str, Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    OTRO = "otro"


class UnidadMedidaEnum(str, Enum):
    UNIDAD = "unidad"
    KG = "kg"
    LITRO = "litro"
    METRO = "metro"
    CAJA = "caja"


# ==============================================
# CATEGORIA SCHEMAS
# ==============================================


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: bool = True


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class Categoria(CategoriaBase):
    id_categoria: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==============================================
# PROVEEDOR SCHEMAS
# ==============================================


class ProveedorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class Proveedor(ProveedorBase):
    id_proveedor: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==============================================
# CLIENTE SCHEMAS
# ==============================================


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class Cliente(ClienteBase):
    id_cliente: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==============================================
# PRODUCTO SCHEMAS
# ==============================================


class ProductoBase(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    id_categoria: int = Field(..., gt=0)
    precio_actual: float = Field(..., ge=0)
    precio_costo: Optional[float] = Field(None, ge=0)
    stock_minimo: int = Field(default=0, ge=0)
    stock: int = Field(default=0, ge=0)
    unidad_medida: UnidadMedidaEnum = UnidadMedidaEnum.UNIDAD
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    id_categoria: Optional[int] = Field(None, gt=0)
    precio_actual: Optional[float] = Field(None, ge=0)
    precio_costo: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    unidad_medida: Optional[UnidadMedidaEnum] = None
    activo: Optional[bool] = None


class Producto(ProductoBase):
    id_producto: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    categoria: Optional[Categoria] = None  # Relación con categoría

    class Config:
        from_attributes = True


class ProductoConStock(Producto):
    """Schema extendido con información de stock y alertas"""

    necesita_reposicion: bool = False

    @field_validator("necesita_reposicion", mode="before")
    @classmethod
    def calcular_necesita_reposicion(cls, v, info):
        stock = info.data.get("stock", 0)
        stock_minimo = info.data.get("stock_minimo", 0)
        return stock <= stock_minimo


# ==============================================
# DETALLE COMPRA SCHEMAS
# ==============================================


class DetalleCompraBase(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., ge=0)


class DetalleCompraCreate(DetalleCompraBase):
    pass


class DetalleCompra(DetalleCompraBase):
    id_detalle_compra: int
    id_compra: int
    subtotal: float
    producto: Optional[Producto] = None  # Relación con producto

    class Config:
        from_attributes = True


# ==============================================
# COMPRA SCHEMAS
# ==============================================


class CompraBase(BaseModel):
    numero_factura: Optional[str] = Field(None, max_length=50)
    id_proveedor: Optional[int] = Field(None, gt=0)
    fecha: datetime = Field(default_factory=datetime.now)
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADA


class CompraCreate(CompraBase):
    detalles: List[DetalleCompraCreate] = Field(..., min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_detalles(cls, v):
        if not v:
            raise ValueError("Debe incluir al menos un detalle de compra")
        return v


class CompraUpdate(BaseModel):
    numero_factura: Optional[str] = Field(None, max_length=50)
    id_proveedor: Optional[int] = Field(None, gt=0)
    observaciones: Optional[str] = None
    estado: Optional[EstadoEnum] = None


class Compra(CompraBase):
    id_compra: int
    total: float
    fecha_creacion: datetime
    proveedor: Optional[Proveedor] = None  # Relación con proveedor
    detalles: List[DetalleCompra] = []  # Relación con detalles

    class Config:
        from_attributes = True


# ==============================================
# DETALLE VENTA SCHEMAS
# ==============================================


class DetalleVentaBase(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., ge=0)
    descuento: float = Field(default=0, ge=0)


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVenta(DetalleVentaBase):
    id_detalle_venta: int
    id_venta: int
    subtotal: float
    producto: Optional[Producto] = None  # Relación con producto

    class Config:
        from_attributes = True


# ==============================================
# VENTA SCHEMAS
# ==============================================


class VentaBase(BaseModel):
    numero_ticket: Optional[str] = Field(None, max_length=50)
    id_cliente: Optional[int] = Field(None, gt=0)
    fecha: datetime = Field(default_factory=datetime.now)
    metodo_pago: MetodoPagoEnum = MetodoPagoEnum.EFECTIVO
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADA


class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate] = Field(..., min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_detalles(cls, v):
        if not v:
            raise ValueError("Debe incluir al menos un detalle de venta")
        return v


class VentaUpdate(BaseModel):
    numero_ticket: Optional[str] = Field(None, max_length=50)
    id_cliente: Optional[int] = Field(None, gt=0)
    metodo_pago: Optional[MetodoPagoEnum] = None
    observaciones: Optional[str] = None
    estado: Optional[EstadoEnum] = None


class Venta(VentaBase):
    id_venta: int
    total: float
    fecha_creacion: datetime
    cliente: Optional[Cliente] = None  # Relación con cliente
    detalles: List[DetalleVenta] = []  # Relación con detalles

    class Config:
        from_attributes = True


# ==============================================
# HISTORIAL PRECIO SCHEMAS
# ==============================================


class HistorialPrecioBase(BaseModel):
    id_producto: int = Field(..., gt=0)
    precio_anterior: Optional[float] = Field(None, ge=0)
    precio_nuevo: float = Field(..., ge=0)
    motivo: Optional[str] = Field(None, max_length=100)


class HistorialPrecioCreate(HistorialPrecioBase):
    pass


class HistorialPrecio(HistorialPrecioBase):
    id_historial: int
    fecha_cambio: datetime
    producto: Optional[Producto] = None

    class Config:
        from_attributes = True


# ==============================================
# SCHEMAS PARA REPORTES Y ESTADÍSTICAS
# ==============================================


class ReporteVentasProducto(BaseModel):
    id_producto: int
    nombre_producto: str
    cantidad_vendida: int
    total_vendido: float
    ganancia: float


class ReporteStockBajo(BaseModel):
    id_producto: int
    nombre: str
    codigo: Optional[str]
    stock_actual: int
    stock_minimo: int
    diferencia: int


class ReporteVentasPeriodo(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    total_ventas: float
    cantidad_ventas: int
    ticket_promedio: float
    productos_mas_vendidos: List[ReporteVentasProducto]


class ReporteComprasPeriodo(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime
    total_compras: float
    cantidad_compras: int
    compra_promedio: float


# ==============================================
# SCHEMAS DE RESPUESTA GENÉRICOS
# ==============================================


class MensajeRespuesta(BaseModel):
    mensaje: str
    detalles: Optional[str] = None


class RespuestaPaginada(BaseModel):
    items: List[BaseModel]
    total: int
    pagina: int
    tamano_pagina: int
    total_paginas: int


# ==============================================
# SCHEMAS PARA BÚSQUEDAS Y FILTROS
# ==============================================


class FiltroProducto(BaseModel):
    nombre: Optional[str] = None
    id_categoria: Optional[int] = None
    codigo: Optional[str] = None
    stock_bajo: Optional[bool] = None
    activo: Optional[bool] = None
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None


class FiltroVenta(BaseModel):
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    id_cliente: Optional[int] = None
    metodo_pago: Optional[MetodoPagoEnum] = None
    estado: Optional[EstadoEnum] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None


class FiltroCompra(BaseModel):
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    id_proveedor: Optional[int] = None
    estado: Optional[EstadoEnum] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None

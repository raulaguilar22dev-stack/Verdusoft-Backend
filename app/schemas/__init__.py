"""Schemas de la API. Re-exporta todos los DTOs por dominio."""

# Enums
from app.schemas.enums import EstadoEnum, MetodoPagoEnum, UnidadMedidaEnum

# Genéricos
from app.schemas.generic import MensajeRespuesta, RespuestaPaginada

# Dominios simples (sin referencias circulares)
from app.schemas.categoria import CategoriaBase, CategoriaCreate, CategoriaUpdate, Categoria
from app.schemas.proveedor import ProveedorBase, ProveedorCreate, ProveedorUpdate, Proveedor
from app.schemas.cliente import ClienteBase, ClienteCreate, ClienteUpdate, Cliente

# Dominios con referencias circulares (importar antes de rebuild)
from app.schemas.producto import ProductoBase, ProductoCreate, ProductoUpdate, Producto, ProductoConStock
from app.schemas.compra import DetalleCompraBase, DetalleCompraCreate, DetalleCompra, CompraBase, CompraCreate, CompraUpdate, Compra
from app.schemas.venta import DetalleVentaBase, DetalleVentaCreate, DetalleVenta, VentaBase, VentaCreate, VentaUpdate, Venta
from app.schemas.historial import HistorialPrecioBase, HistorialPrecioCreate, HistorialPrecio

# Reportes y filtros
from app.schemas.reporte import ReporteVentasProducto, ReporteStockBajo, ReporteVentasPeriodo, ReporteComprasPeriodo
from app.schemas.filtros import FiltroProducto, FiltroVenta, FiltroCompra

# Resolver referencias circulares hacia adelante
Producto.model_rebuild()
ProductoConStock.model_rebuild()
DetalleCompra.model_rebuild()
Compra.model_rebuild()
DetalleVenta.model_rebuild()
Venta.model_rebuild()
HistorialPrecio.model_rebuild()

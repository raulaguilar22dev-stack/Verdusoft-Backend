"""Modelos de dominio que reflejan las tablas de la base de datos."""

from app.models.categoria import Categoria
from app.models.proveedor import Proveedor
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.compra import Compra, DetalleCompra
from app.models.venta import Venta, DetalleVenta
from app.models.historial import HistorialPrecio

"""Schemas para reportes y estadísticas."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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

"""Enumeraciones compartidas del dominio."""

from enum import Enum


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

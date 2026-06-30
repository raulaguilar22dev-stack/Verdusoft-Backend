"""Tests unitarios para venta_service."""

from __future__ import annotations

from datetime import datetime

import pytest

from app.schemas.enums import EstadoEnum, MetodoPagoEnum
from app.schemas.venta import VentaCreate, VentaUpdate, DetalleVentaCreate
from app.services import venta_service


class TestListar:
    def test_listar_sin_filtros(self, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|order:fecha:True|range:0:99": {
                "data": [{"id_venta": 1, "total": 50.0}]
            }
        }
        result = venta_service.listar(mock_db)
        assert len(result) == 1

    def test_listar_con_filtros(self, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|gte:fecha:2024-01-01T00:00:00|lte:fecha:2024-12-31T00:00:00|eq:id_cliente:1|eq:metodo_pago:efectivo|eq:estado:completada|order:fecha:True|range:0:99": {
                "data": [{"id_venta": 1}]
            }
        }
        result = venta_service.listar(
            mock_db,
            fecha_inicio=datetime(2024, 1, 1),
            fecha_fin=datetime(2024, 12, 31),
            id_cliente=1,
            metodo_pago="efectivo",
            estado="completada",
        )
        assert len(result) == 1

    def test_listar_data_none(self, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|order:fecha:True|range:0:99": {"data": None}
        }
        result = venta_service.listar(mock_db)
        assert result == []


class TestObtener:
    def test_obtener_con_detalles(self, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|eq:id_venta:1": {
                "data": [{"id_venta": 1, "numero_ticket": "T001"}]
            },
            "table:detalle_venta|select:*, producto(*)|eq:id_venta:1": {
                "data": [{"id_detalle_venta": 1, "cantidad": 1}]
            },
        }
        result = venta_service.obtener(mock_db, 1)
        assert result["id_venta"] == 1
        assert len(result["detalles"]) == 1

    def test_obtener_no_encontrada(self, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|eq:id_venta:99": {"data": []}
        }
        with pytest.raises(ValueError, match="Venta no encontrada"):
            venta_service.obtener(mock_db, 99)


class TestCrear:
    def test_crear_llama_rpc_crear_venta(self, mock_db):
        mock_db.responses = {
            "rpc:crear_venta": {"data": [{"id_venta": 42}]},
            "table:venta|select:*, cliente(*)|eq:id_venta:42": {
                "data": [{"id_venta": 42, "numero_ticket": "T001"}]
            },
            "table:detalle_venta|select:*, producto(*)|eq:id_venta:42": {"data": []},
        }
        venta = VentaCreate(
            numero_ticket="T001",
            id_cliente=1,
            fecha=datetime(2024, 6, 1),
            metodo_pago=MetodoPagoEnum.EFECTIVO,
            observaciones="Test",
            estado=EstadoEnum.COMPLETADA,
            detalles=[
                DetalleVentaCreate(id_producto=1, cantidad=1, precio_unitario=10.0)
            ],
        )
        result = venta_service.crear(mock_db, venta)
        assert result["id_venta"] == 42

        rpc_calls = [c for c in mock_db.calls if c["type"] == "rpc"]
        assert len(rpc_calls) == 1
        assert rpc_calls[0]["func"] == "crear_venta"
        assert rpc_calls[0]["params"]["p_numero_ticket"] == "T001"
        assert rpc_calls[0]["params"]["p_id_cliente"] == 1
        assert rpc_calls[0]["params"]["p_metodo_pago"] == "efectivo"
        assert rpc_calls[0]["params"]["p_estado"] == "completada"
        import json

        detalles = json.loads(rpc_calls[0]["params"]["p_detalles"])
        assert len(detalles) == 1
        assert detalles[0]["id_producto"] == 1

    def test_crear_rpc_sin_data(self, mock_db):
        mock_db.responses = {"rpc:crear_venta": {"data": []}}
        venta = VentaCreate(
            numero_ticket="T002",
            id_cliente=1,
            fecha=datetime(2024, 6, 1),
            metodo_pago=MetodoPagoEnum.EFECTIVO,
            estado=EstadoEnum.COMPLETADA,
            detalles=[
                DetalleVentaCreate(id_producto=1, cantidad=1, precio_unitario=5.0)
            ],
        )
        with pytest.raises(ValueError, match="Error al crear venta via RPC"):
            venta_service.crear(mock_db, venta)

    def test_crear_rpc_sin_id_venta(self, mock_db):
        mock_db.responses = {"rpc:crear_venta": {"data": [{"unexpected": True}]}}
        venta = VentaCreate(
            numero_ticket="T003",
            id_cliente=1,
            fecha=datetime(2024, 6, 1),
            metodo_pago=MetodoPagoEnum.EFECTIVO,
            estado=EstadoEnum.COMPLETADA,
            detalles=[
                DetalleVentaCreate(id_producto=1, cantidad=1, precio_unitario=5.0)
            ],
        )
        with pytest.raises(ValueError, match="Respuesta inesperada del RPC crear_venta"):
            venta_service.crear(mock_db, venta)


class TestActualizar:
    def test_actualizar_exitoso(self, mock_db):
        mock_db.responses = {
            "table:venta|update|eq:id_venta:1": {"data": [{"id_venta": 1}]},
            "table:venta|select:*, cliente(*)|eq:id_venta:1": {
                "data": [{"id_venta": 1, "observaciones": "Mod"}]
            },
            "table:detalle_venta|select:*, producto(*)|eq:id_venta:1": {"data": []},
        }
        schema = VentaUpdate(observaciones="Mod")
        result = venta_service.actualizar(mock_db, 1, schema)
        assert result["observaciones"] == "Mod"

    def test_actualizar_sin_datos(self, mock_db):
        schema = VentaUpdate()
        with pytest.raises(ValueError, match="No hay datos para actualizar"):
            venta_service.actualizar(mock_db, 1, schema)

    def test_actualizar_no_encontrada(self, mock_db):
        mock_db.responses = {"table:venta|update|eq:id_venta:99": {"data": []}}
        schema = VentaUpdate(observaciones="X")
        with pytest.raises(ValueError, match="Venta no encontrada"):
            venta_service.actualizar(mock_db, 99, schema)


class TestCancelar:
    def test_cancelar_llama_rpc(self, mock_db):
        mock_db.responses = {"rpc:cancelar_venta": {"data": [{"ok": True}]}}
        result = venta_service.cancelar(mock_db, 1)
        assert result["mensaje"] == "Venta cancelada exitosamente"
        rpc_calls = [c for c in mock_db.calls if c["type"] == "rpc"]
        assert rpc_calls[0]["func"] == "cancelar_venta"
        assert rpc_calls[0]["params"] == {"p_id_venta": 1}

    def test_cancelar_rpc_sin_data(self, mock_db):
        mock_db.responses = {"rpc:cancelar_venta": {"data": []}}
        with pytest.raises(ValueError, match="Error al cancelar venta via RPC"):
            venta_service.cancelar(mock_db, 1)

"""Tests unitarios para compra_service."""

from __future__ import annotations

from datetime import datetime

import pytest

from app.schemas.compra import CompraCreate, CompraUpdate, DetalleCompraCreate
from app.schemas.enums import EstadoEnum
from app.services import compra_service


class TestListar:
    def test_listar_sin_filtros(self, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|order:fecha:True|range:0:99": {
                "data": [{"id_compra": 1, "total": 100.0}]
            }
        }
        result = compra_service.listar(mock_db)
        assert len(result) == 1

    def test_listar_con_filtros(self, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|gte:fecha:2024-01-01T00:00:00|lte:fecha:2024-12-31T00:00:00|eq:id_proveedor:1|eq:estado:completada|order:fecha:True|range:0:99": {
                "data": [{"id_compra": 1}]
            }
        }
        result = compra_service.listar(
            mock_db,
            fecha_inicio=datetime(2024, 1, 1),
            fecha_fin=datetime(2024, 12, 31),
            id_proveedor=1,
            estado="completada",
        )
        assert len(result) == 1

    def test_listar_data_none(self, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|order:fecha:True|range:0:99": {
                "data": None
            }
        }
        result = compra_service.listar(mock_db)
        assert result == []


class TestObtener:
    def test_obtener_con_detalles(self, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|eq:id_compra:1": {
                "data": [{"id_compra": 1, "numero_factura": "F001"}]
            },
            "table:detalle_compra|select:*, producto(*)|eq:id_compra:1": {
                "data": [{"id_detalle_compra": 1, "cantidad": 2}]
            },
        }
        result = compra_service.obtener(mock_db, 1)
        assert result["id_compra"] == 1
        assert len(result["detalles"]) == 1

    def test_obtener_no_encontrada(self, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|eq:id_compra:99": {"data": []}
        }
        with pytest.raises(ValueError, match="Compra no encontrada"):
            compra_service.obtener(mock_db, 99)


class TestCrear:
    def test_crear_llama_rpc_crear_compra(self, mock_db):
        mock_db.responses = {
            "rpc:crear_compra": {"data": [{"id_compra": 42}]},
            "table:compra|select:*, proveedor(*)|eq:id_compra:42": {
                "data": [{"id_compra": 42, "numero_factura": "F001"}]
            },
            "table:detalle_compra|select:*, producto(*)|eq:id_compra:42": {"data": []},
        }
        compra = CompraCreate(
            numero_factura="F001",
            id_proveedor=1,
            fecha=datetime(2024, 6, 1),
            observaciones="Test",
            estado=EstadoEnum.COMPLETADA,
            detalles=[
                DetalleCompraCreate(id_producto=1, cantidad=2, precio_unitario=10.0)
            ],
        )
        result = compra_service.crear(mock_db, compra)
        assert result["id_compra"] == 42

        rpc_calls = [c for c in mock_db.calls if c["type"] == "rpc"]
        assert len(rpc_calls) == 1
        assert rpc_calls[0]["func"] == "crear_compra"
        assert rpc_calls[0]["params"]["p_numero_factura"] == "F001"
        assert rpc_calls[0]["params"]["p_id_proveedor"] == 1
        assert rpc_calls[0]["params"]["p_estado"] == "completada"
        # Verificar que los detalles se serializan como JSON string
        import json
        detalles = json.loads(rpc_calls[0]["params"]["p_detalles"])
        assert len(detalles) == 1
        assert detalles[0]["id_producto"] == 1

    def test_crear_rpc_sin_data(self, mock_db):
        mock_db.responses = {"rpc:crear_compra": {"data": []}}
        compra = CompraCreate(
            numero_factura="F002",
            id_proveedor=1,
            fecha=datetime(2024, 6, 1),
            estado=EstadoEnum.COMPLETADA,
            detalles=[
                DetalleCompraCreate(id_producto=1, cantidad=1, precio_unitario=5.0)
            ],
        )
        with pytest.raises(ValueError, match="Error al crear compra via RPC"):
            compra_service.crear(mock_db, compra)

    def test_crear_rpc_sin_id_compra(self, mock_db):
        mock_db.responses = {"rpc:crear_compra": {"data": [{"unexpected": True}]}}
        compra = CompraCreate(
            numero_factura="F003",
            id_proveedor=1,
            fecha=datetime(2024, 6, 1),
            estado=EstadoEnum.COMPLETADA,
            detalles=[
                DetalleCompraCreate(id_producto=1, cantidad=1, precio_unitario=5.0)
            ],
        )
        with pytest.raises(ValueError, match="Respuesta inesperada del RPC crear_compra"):
            compra_service.crear(mock_db, compra)


class TestActualizar:
    def test_actualizar_exitoso(self, mock_db):
        mock_db.responses = {
            "table:compra|update|eq:id_compra:1": {"data": [{"id_compra": 1}]},
            "table:compra|select:*, proveedor(*)|eq:id_compra:1": {
                "data": [{"id_compra": 1, "observaciones": "Mod"}]
            },
            "table:detalle_compra|select:*, producto(*)|eq:id_compra:1": {"data": []},
        }
        schema = CompraUpdate(observaciones="Mod")
        result = compra_service.actualizar(mock_db, 1, schema)
        assert result["observaciones"] == "Mod"

    def test_actualizar_sin_datos(self, mock_db):
        schema = CompraUpdate()
        with pytest.raises(ValueError, match="No hay datos para actualizar"):
            compra_service.actualizar(mock_db, 1, schema)

    def test_actualizar_no_encontrada(self, mock_db):
        mock_db.responses = {"table:compra|update|eq:id_compra:99": {"data": []}}
        schema = CompraUpdate(observaciones="X")
        with pytest.raises(ValueError, match="Compra no encontrada"):
            compra_service.actualizar(mock_db, 99, schema)


class TestCancelar:
    def test_cancelar_llama_rpc(self, mock_db):
        mock_db.responses = {"rpc:cancelar_compra": {"data": [{"ok": True}]}}
        result = compra_service.cancelar(mock_db, 1)
        assert result["mensaje"] == "Compra cancelada exitosamente"
        rpc_calls = [c for c in mock_db.calls if c["type"] == "rpc"]
        assert rpc_calls[0]["func"] == "cancelar_compra"
        assert rpc_calls[0]["params"] == {"p_id_compra": 1}

    def test_cancelar_rpc_sin_data(self, mock_db):
        mock_db.responses = {"rpc:cancelar_compra": {"data": []}}
        with pytest.raises(ValueError, match="Error al cancelar compra via RPC"):
            compra_service.cancelar(mock_db, 1)

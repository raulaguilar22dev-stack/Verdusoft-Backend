"""Tests unitarios para producto_service."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from postgrest.exceptions import APIError

from app.schemas.enums import UnidadMedidaEnum
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.services import producto_service


class TestListar:
    def test_listar_sin_filtros(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|order:nombre:False|range:0:99": {
                "data": [{"id_producto": 1, "nombre": "Prod"}]
            }
        }
        result = producto_service.listar(mock_db)
        assert len(result) == 1

    def test_listar_con_nombre(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|ilike:nombre:%test%|order:nombre:False|range:0:99": {
                "data": [{"id_producto": 1, "nombre": "Test"}]
            }
        }
        result = producto_service.listar(mock_db, nombre="test")
        assert len(result) == 1

    def test_listar_con_categoria(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:id_categoria:1|order:nombre:False|range:0:99": {
                "data": [{"id_producto": 1, "nombre": "Cat"}]
            }
        }
        result = producto_service.listar(mock_db, id_categoria=1)
        assert len(result) == 1

    def test_listar_con_codigo(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:codigo:ABC123|order:nombre:False|range:0:99": {
                "data": [{"id_producto": 1, "codigo": "ABC123"}]
            }
        }
        result = producto_service.listar(mock_db, codigo="ABC123")
        assert len(result) == 1

    def test_listar_con_activo(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:activo:False|order:nombre:False|range:0:99": {
                "data": [{"id_producto": 1, "activo": False}]
            }
        }
        result = producto_service.listar(mock_db, activo=False)
        assert len(result) == 1

    def test_listar_con_stock_bajo_usa_vw(self, mock_db):
        mock_db.responses = {
            "table:vw_stock_bajo|select:*": {
                "data": [{"id_producto": 1, "nombre": "Bajo"}]
            }
        }
        result = producto_service.listar(mock_db, stock_bajo=True)
        assert len(result) == 1
        assert mock_db.calls[0]["type"] == "query"
        assert mock_db.calls[0]["table"] == "vw_stock_bajo"


class TestCatalogo:
    def test_catalogo(self, mock_db):
        mock_db.responses = {
            "table:producto|select:id_producto, nombre, precio_actual|eq:activo:True|order:nombre:False": {
                "data": [{"id_producto": 1, "nombre": "Cat", "precio_actual": 10.0}]
            }
        }
        result = producto_service.catalogo(mock_db)
        assert len(result) == 1
        assert result[0]["precio_actual"] == 10.0


class TestStockBajo:
    def test_stock_bajo(self, mock_db):
        mock_db.responses = {
            "table:vw_stock_bajo|select:*": {
                "data": [{"id_producto": 1, "nombre": "Bajo"}]
            }
        }
        result = producto_service.stock_bajo(mock_db)
        assert len(result) == 1


class TestObtener:
    def test_obtener_existente(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:id_producto:1": {
                "data": [{"id_producto": 1, "nombre": "P"}]
            }
        }
        result = producto_service.obtener(mock_db, 1)
        assert result["nombre"] == "P"

    def test_obtener_no_encontrado(self, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:id_producto:99": {"data": []}
        }
        with pytest.raises(ValueError, match="Producto no encontrado"):
            producto_service.obtener(mock_db, 99)


class TestCrear:
    def test_crear_exitoso(self, mock_db):
        mock_db.responses = {
            "table:producto|insert": {"data": [{"id_producto": 1, "nombre": "Nuevo"}]}
        }
        schema = ProductoCreate(
            nombre="Nuevo",
            id_categoria=1,
            precio_actual=10.0,
            stock=5,
            unidad_medida=UnidadMedidaEnum.UNIDAD,
        )
        result = producto_service.crear(mock_db, schema)
        assert result["id_producto"] == 1

    def test_crear_duplicate_code(self):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = APIError(
            {"message": "duplicate key value violates unique constraint"}
        )
        schema = ProductoCreate(
            nombre="Dup",
            id_categoria=1,
            precio_actual=10.0,
            stock=5,
            unidad_medida=UnidadMedidaEnum.UNIDAD,
        )
        with pytest.raises(ValueError, match="Ya existe un producto con ese codigo"):
            producto_service.crear(db, schema)

    def test_crear_error_generico(self):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = APIError({"message": "some random error"})
        schema = ProductoCreate(
            nombre="Err",
            id_categoria=1,
            precio_actual=10.0,
            stock=5,
            unidad_medida=UnidadMedidaEnum.UNIDAD,
        )
        with pytest.raises(ValueError, match="Error al crear producto"):
            producto_service.crear(db, schema)


class TestActualizar:
    def test_actualizar_exitoso(self, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:1": {
                "data": [{"id_producto": 1, "nombre": "Mod"}]
            }
        }
        schema = ProductoUpdate(nombre="Mod")
        result = producto_service.actualizar(mock_db, 1, schema)
        assert result["nombre"] == "Mod"

    def test_actualizar_sin_datos(self, mock_db):
        schema = ProductoUpdate()
        with pytest.raises(ValueError, match="No hay datos para actualizar"):
            producto_service.actualizar(mock_db, 1, schema)

    def test_actualizar_no_encontrado(self, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:99": {"data": []}
        }
        schema = ProductoUpdate(nombre="X")
        with pytest.raises(ValueError, match="Producto no encontrado"):
            producto_service.actualizar(mock_db, 99, schema)


class TestEliminar:
    def test_eliminar_soft_delete(self, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:1": {"data": [{"id_producto": 1}]}
        }
        result = producto_service.eliminar(mock_db, 1)
        assert result["mensaje"] == "Producto desactivado exitosamente"

    def test_eliminar_no_encontrado(self, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:99": {"data": []}
        }
        with pytest.raises(ValueError, match="Producto no encontrado"):
            producto_service.eliminar(mock_db, 99)

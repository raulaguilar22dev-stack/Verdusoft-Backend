"""Tests unitarios para BaseCRUDService."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from postgrest.exceptions import APIError
from unittest.mock import MagicMock

from app.services.base_service import BaseCRUDService
from tests.conftest import MockSupabase


class DummyCreate(BaseModel):
    nombre: str


class DummyUpdate(BaseModel):
    nombre: str | None = None


@pytest.fixture
def service():
    return BaseCRUDService("dummy", "id_dummy", orden="nombre")


class TestListar:
    def test_listar_sin_filtros(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|select:*|order:nombre:False|range:0:99": {
                "data": [{"id_dummy": 1, "nombre": "A"}, {"id_dummy": 2, "nombre": "B"}]
            }
        }
        result = service.listar(mock_db)
        assert len(result) == 2
        assert result[0]["nombre"] == "A"
        assert mock_db.calls[0]["key"] == "table:dummy|select:*|order:nombre:False|range:0:99"

    def test_listar_con_activo(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|select:*|eq:activo:True|order:nombre:False|range:0:99": {
                "data": [{"id_dummy": 1, "nombre": "A"}]
            }
        }
        result = service.listar(mock_db, activo=True)
        assert len(result) == 1

    def test_listar_paginacion(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|select:*|order:nombre:False|range:10:19": {"data": []}
        }
        service.listar(mock_db, skip=10, limit=10)
        assert mock_db.calls[0]["key"].endswith("range:10:19")

    def test_listar_data_none(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|select:*|order:nombre:False|range:0:99": {"data": None}
        }
        result = service.listar(mock_db)
        assert result == []


class TestObtener:
    def test_obtener_existente(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|select:*|eq:id_dummy:1": {"data": [{"id_dummy": 1, "nombre": "A"}]}
        }
        result = service.obtener(mock_db, 1)
        assert result["id_dummy"] == 1

    def test_obtener_no_existente(self, service, mock_db):
        mock_db.responses = {"table:dummy|select:*|eq:id_dummy:99": {"data": []}}
        with pytest.raises(ValueError, match="Dummy no encontrado/a"):
            service.obtener(mock_db, 99)


class TestCrear:
    def test_crear_exitoso(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|insert": {"data": [{"id_dummy": 1, "nombre": "Nuevo"}]}
        }
        schema = DummyCreate(nombre="Nuevo")
        result = service.crear(mock_db, schema)
        assert result["id_dummy"] == 1
        assert mock_db.calls[0]["insert_data"] == {"nombre": "Nuevo"}

    def test_crear_con_error_handler(self, service):
        def handler(e: APIError):
            if "duplicate" in str(e).lower():
                return ValueError("Duplicado")
            return None

        svc = BaseCRUDService("dummy", "id_dummy", error_handler=handler)
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = APIError(
            {"message": "duplicate key value violates unique constraint"}
        )

        schema = DummyCreate(nombre="Dup")
        with pytest.raises(ValueError, match="Duplicado"):
            svc.crear(db, schema)

    def test_crear_sin_error_handler(self, service):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = APIError({"message": "random error"})

        schema = DummyCreate(nombre="X")
        with pytest.raises(ValueError, match="Error al crear dummy"):
            service.crear(db, schema)

    def test_crear_error_inesperado(self, service):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = RuntimeError("boom")

        schema = DummyCreate(nombre="X")
        with pytest.raises(ValueError, match="Error al crear dummy"):
            service.crear(db, schema)


class TestActualizar:
    def test_actualizar_exitoso(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|update|eq:id_dummy:1": {"data": [{"id_dummy": 1, "nombre": "Mod"}]}
        }
        schema = DummyUpdate(nombre="Mod")
        result = service.actualizar(mock_db, 1, schema)
        assert result["nombre"] == "Mod"
        assert mock_db.calls[0]["update_data"] == {"nombre": "Mod"}

    def test_actualizar_sin_datos(self, service, mock_db):
        schema = DummyUpdate()
        with pytest.raises(ValueError, match="No hay datos para actualizar"):
            service.actualizar(mock_db, 1, schema)

    def test_actualizar_no_encontrado(self, service, mock_db):
        mock_db.responses = {"table:dummy|update|eq:id_dummy:99": {"data": []}}
        schema = DummyUpdate(nombre="X")
        with pytest.raises(ValueError, match="Dummy no encontrado/a"):
            service.actualizar(mock_db, 99, schema)


class TestEliminar:
    def test_eliminar_soft_delete(self, service, mock_db):
        mock_db.responses = {
            "table:dummy|update|eq:id_dummy:1": {"data": [{"id_dummy": 1}]}
        }
        result = service.eliminar(mock_db, 1)
        assert result["mensaje"] == "Dummy desactivado/a exitosamente"
        assert mock_db.calls[0]["update_data"] == {"activo": False}

    def test_eliminar_no_encontrado(self, service, mock_db):
        mock_db.responses = {"table:dummy|update|eq:id_dummy:99": {"data": []}}
        with pytest.raises(ValueError, match="Dummy no encontrado/a"):
            service.eliminar(mock_db, 99)

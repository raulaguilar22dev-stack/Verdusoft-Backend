"""Tests de integracion para el router de Categorias."""

from __future__ import annotations

from unittest.mock import MagicMock

from postgrest.exceptions import APIError

FECHA = "2024-01-01T00:00:00"


def _categoria_data(id_=1, nombre="Test"):
    return {
        "id_categoria": id_,
        "nombre": nombre,
        "descripcion": None,
        "activo": True,
        "fecha_creacion": FECHA,
    }


class TestListarCategorias:
    def test_listar_admin(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|select:*|order:nombre:False|range:0:99": {
                "data": [_categoria_data(), _categoria_data(id_=2, nombre="Otra")]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/categorias", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["nombre"] == "Test"

    def test_sin_auth(self, client):
        response = client.get("/api/categorias")
        assert response.status_code == 401

    def test_rol_publico(self, client, public_token, override_db, mock_db):
        override_db(mock_db)
        response = client.get(
            "/api/categorias", headers={"Authorization": f"Bearer {public_token}"}
        )
        assert response.status_code == 403


class TestObtenerCategoria:
    def test_obtener_existente(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|select:*|eq:id_categoria:1": {
                "data": [_categoria_data()]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/categorias/1", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Test"

    def test_obtener_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|select:*|eq:id_categoria:99": {"data": []}
        }
        override_db(mock_db)
        response = client.get(
            "/api/categorias/99", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
        assert "no encontrado" in response.json()["mensaje"]


class TestCrearCategoria:
    def test_crear_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|insert": {
                "data": [_categoria_data(id_=2, nombre="Nueva")]
            }
        }
        override_db(mock_db)
        response = client.post(
            "/api/categorias",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nombre": "Nueva", "activo": True},
        )
        assert response.status_code == 201
        assert response.json()["nombre"] == "Nueva"

    def test_crear_bad_request(self, client, admin_token, override_db, mock_db):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = APIError(
            {"message": "duplicate key value violates unique constraint"}
        )
        override_db(db)
        response = client.post(
            "/api/categorias",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nombre": "Duplicada", "activo": True},
        )
        assert response.status_code == 400
        assert "Ya existe" in response.json()["mensaje"]


class TestActualizarCategoria:
    def test_actualizar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|update|eq:id_categoria:1": {
                "data": [_categoria_data(nombre="Modificada")]
            }
        }
        override_db(mock_db)
        response = client.patch(
            "/api/categorias/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nombre": "Modificada"},
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Modificada"

    def test_actualizar_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|update|eq:id_categoria:99": {"data": []}
        }
        override_db(mock_db)
        response = client.patch(
            "/api/categorias/99",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nombre": "X"},
        )
        assert response.status_code == 404


class TestEliminarCategoria:
    def test_eliminar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|update|eq:id_categoria:1": {"data": [{"id_categoria": 1}]}
        }
        override_db(mock_db)
        response = client.delete(
            "/api/categorias/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert "desactivado/a" in response.json()["mensaje"]

    def test_eliminar_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:categoria|update|eq:id_categoria:99": {"data": []}
        }
        override_db(mock_db)
        response = client.delete(
            "/api/categorias/99",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

"""Tests de integracion para el router de Productos."""

from __future__ import annotations

from unittest.mock import MagicMock

from postgrest.exceptions import APIError

FECHA = "2024-01-01T00:00:00"


def _producto_data(id_=1, nombre="Producto"):
    return {
        "id_producto": id_,
        "codigo": f"COD{id_}",
        "nombre": nombre,
        "descripcion": "Desc",
        "id_categoria": 1,
        "precio_actual": 10.0,
        "precio_costo": 5.0,
        "stock_minimo": 2,
        "stock": 10,
        "unidad_medida": "unidad",
        "activo": True,
        "fecha_creacion": FECHA,
        "fecha_actualizacion": FECHA,
    }


class TestCatalogoPublico:
    def test_catalogo_sin_auth(self, client, override_db, mock_db):
        mock_db.responses = {
            "table:producto|select:id_producto, nombre, precio_actual|eq:activo:True|order:nombre:False": {
                "data": [
                    {"id_producto": 1, "nombre": "Pub", "precio_actual": 15.0}
                ]
            }
        }
        override_db(mock_db)
        response = client.get("/api/productos/catalogo")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["precio_actual"] == 15.0


class TestListarProductos:
    def test_listar_admin(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|order:nombre:False|range:0:99": {
                "data": [_producto_data()]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/productos", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_sin_auth(self, client):
        response = client.get("/api/productos")
        assert response.status_code == 401

    def test_rol_publico(self, client, public_token, override_db, mock_db):
        override_db(mock_db)
        response = client.get(
            "/api/productos", headers={"Authorization": f"Bearer {public_token}"}
        )
        assert response.status_code == 403


class TestStockBajo:
    def test_stock_bajo_admin(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:vw_stock_bajo|select:*": {
                "data": [
                    {
                        "id_producto": 1,
                        "nombre": "Bajo",
                        "codigo": "B001",
                        "stock_actual": 1,
                        "stock_minimo": 5,
                        "diferencia": 4,
                    }
                ]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/productos/stock-bajo",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_stock_bajo_sin_auth(self, client):
        response = client.get("/api/productos/stock-bajo")
        assert response.status_code == 401


class TestObtenerProducto:
    def test_obtener_existente(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:id_producto:1": {
                "data": [_producto_data()]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/productos/1", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Producto"

    def test_obtener_no_encontrado(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|select:*, categoria(*)|eq:id_producto:99": {"data": []}
        }
        override_db(mock_db)
        response = client.get(
            "/api/productos/99", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestCrearProducto:
    def test_crear_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|insert": {
                "data": [_producto_data(id_=2, nombre="Nuevo")]
            }
        }
        override_db(mock_db)
        response = client.post(
            "/api/productos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nombre": "Nuevo",
                "id_categoria": 1,
                "precio_actual": 10.0,
                "stock": 5,
                "unidad_medida": "unidad",
            },
        )
        assert response.status_code == 201
        assert response.json()["nombre"] == "Nuevo"

    def test_crear_bad_request(self, client, admin_token, override_db, mock_db):
        db = MagicMock()
        db.table.return_value.insert.return_value.execute.side_effect = APIError(
            {"message": "duplicate key value violates unique constraint"}
        )
        override_db(db)
        response = client.post(
            "/api/productos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "nombre": "Dup",
                "id_categoria": 1,
                "precio_actual": 10.0,
                "stock": 5,
                "unidad_medida": "unidad",
            },
        )
        assert response.status_code == 400


class TestActualizarProducto:
    def test_actualizar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:1": {
                "data": [_producto_data(nombre="Mod")]
            }
        }
        override_db(mock_db)
        response = client.patch(
            "/api/productos/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nombre": "Mod"},
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Mod"

    def test_actualizar_no_encontrado(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:99": {"data": []}
        }
        override_db(mock_db)
        response = client.patch(
            "/api/productos/99",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nombre": "Mod"},
        )
        assert response.status_code == 404


class TestEliminarProducto:
    def test_eliminar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:1": {"data": [{"id_producto": 1}]}
        }
        override_db(mock_db)
        response = client.delete(
            "/api/productos/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert "desactivado" in response.json()["mensaje"]

    def test_eliminar_no_encontrado(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:producto|update|eq:id_producto:99": {"data": []}
        }
        override_db(mock_db)
        response = client.delete(
            "/api/productos/99",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

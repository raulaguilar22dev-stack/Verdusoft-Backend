"""Tests de integracion para el router de Compras."""

from __future__ import annotations

FECHA = "2024-01-01T00:00:00"


def _compra_data(id_=1):
    return {
        "id_compra": id_,
        "numero_factura": f"F{id_:03d}",
        "id_proveedor": 1,
        "fecha": FECHA,
        "observaciones": None,
        "estado": "completada",
        "total": 200.0,
        "fecha_creacion": FECHA,
    }


class TestListarCompras:
    def test_listar_admin(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|order:fecha:True|range:0:99": {
                "data": [_compra_data()]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/compras", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_sin_auth(self, client):
        response = client.get("/api/compras")
        assert response.status_code == 401

    def test_rol_publico(self, client, public_token, override_db, mock_db):
        override_db(mock_db)
        response = client.get(
            "/api/compras", headers={"Authorization": f"Bearer {public_token}"}
        )
        assert response.status_code == 403


class TestObtenerCompra:
    def test_obtener_existente(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|eq:id_compra:1": {
                "data": [_compra_data()]
            },
            "table:detalle_compra|select:*, producto(*)|eq:id_compra:1": {
                "data": []
            },
        }
        override_db(mock_db)
        response = client.get(
            "/api/compras/1", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["id_compra"] == 1

    def test_obtener_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:compra|select:*, proveedor(*)|eq:id_compra:99": {"data": []}
        }
        override_db(mock_db)
        response = client.get(
            "/api/compras/99", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestCrearCompra:
    def test_crear_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "rpc:crear_compra": {"data": [{"id_compra": 42}]},
            "table:compra|select:*, proveedor(*)|eq:id_compra:42": {
                "data": [_compra_data(id_=42)]
            },
            "table:detalle_compra|select:*, producto(*)|eq:id_compra:42": {
                "data": []
            },
        }
        override_db(mock_db)
        response = client.post(
            "/api/compras",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "numero_factura": "F001",
                "id_proveedor": 1,
                "fecha": FECHA,
                "estado": "completada",
                "detalles": [
                    {"id_producto": 1, "cantidad": 2, "precio_unitario": 10.0}
                ],
            },
        )
        assert response.status_code == 201
        assert response.json()["id_compra"] == 42

    def test_crear_bad_request(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {"rpc:crear_compra": {"data": []}}
        override_db(mock_db)
        response = client.post(
            "/api/compras",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "numero_factura": "F002",
                "fecha": FECHA,
                "estado": "completada",
                "detalles": [
                    {"id_producto": 1, "cantidad": 1, "precio_unitario": 5.0}
                ],
            },
        )
        assert response.status_code == 400


class TestActualizarCompra:
    def test_actualizar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:compra|update|eq:id_compra:1": {"data": [_compra_data()]},
            "table:compra|select:*, proveedor(*)|eq:id_compra:1": {
                "data": [{**_compra_data(), "observaciones": "Mod"}]
            },
            "table:detalle_compra|select:*, producto(*)|eq:id_compra:1": {
                "data": []
            },
        }
        override_db(mock_db)
        response = client.patch(
            "/api/compras/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"observaciones": "Mod"},
        )
        assert response.status_code == 200
        assert response.json()["observaciones"] == "Mod"

    def test_actualizar_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:compra|update|eq:id_compra:99": {"data": []}
        }
        override_db(mock_db)
        response = client.patch(
            "/api/compras/99",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"observaciones": "Mod"},
        )
        assert response.status_code == 404


class TestCancelarCompra:
    def test_cancelar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {"rpc:cancelar_compra": {"data": [{"ok": True}]}}
        override_db(mock_db)
        response = client.delete(
            "/api/compras/1", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "cancelada" in response.json()["mensaje"]

    def test_cancelar_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {"rpc:cancelar_compra": {"data": []}}
        override_db(mock_db)
        response = client.delete(
            "/api/compras/99", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

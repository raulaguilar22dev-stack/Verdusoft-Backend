"""Tests de integracion para el router de Ventas."""

from __future__ import annotations

FECHA = "2024-01-01T00:00:00"


def _venta_data(id_=1):
    return {
        "id_venta": id_,
        "numero_ticket": f"T{id_:03d}",
        "id_cliente": 1,
        "fecha": FECHA,
        "metodo_pago": "efectivo",
        "observaciones": None,
        "estado": "completada",
        "total": 100.0,
        "fecha_creacion": FECHA,
    }


class TestListarVentas:
    def test_listar_admin(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|order:fecha:True|range:0:99": {
                "data": [_venta_data()]
            }
        }
        override_db(mock_db)
        response = client.get(
            "/api/ventas", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_sin_auth(self, client):
        response = client.get("/api/ventas")
        assert response.status_code == 401

    def test_rol_publico(self, client, public_token, override_db, mock_db):
        override_db(mock_db)
        response = client.get(
            "/api/ventas", headers={"Authorization": f"Bearer {public_token}"}
        )
        assert response.status_code == 403


class TestObtenerVenta:
    def test_obtener_existente(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|eq:id_venta:1": {
                "data": [_venta_data()]
            },
            "table:detalle_venta|select:*, producto(*)|eq:id_venta:1": {"data": []},
        }
        override_db(mock_db)
        response = client.get(
            "/api/ventas/1", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["id_venta"] == 1

    def test_obtener_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:venta|select:*, cliente(*)|eq:id_venta:99": {"data": []}
        }
        override_db(mock_db)
        response = client.get(
            "/api/ventas/99", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404


class TestCrearVenta:
    def test_crear_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "rpc:crear_venta": {"data": [{"id_venta": 42}]},
            "table:venta|select:*, cliente(*)|eq:id_venta:42": {
                "data": [_venta_data(id_=42)]
            },
            "table:detalle_venta|select:*, producto(*)|eq:id_venta:42": {"data": []},
        }
        override_db(mock_db)
        response = client.post(
            "/api/ventas",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "numero_ticket": "T001",
                "id_cliente": 1,
                "fecha": FECHA,
                "metodo_pago": "efectivo",
                "estado": "completada",
                "detalles": [
                    {"id_producto": 1, "cantidad": 2, "precio_unitario": 10.0}
                ],
            },
        )
        assert response.status_code == 201
        assert response.json()["id_venta"] == 42

    def test_crear_bad_request(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {"rpc:crear_venta": {"data": []}}
        override_db(mock_db)
        response = client.post(
            "/api/ventas",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "numero_ticket": "T002",
                "fecha": FECHA,
                "metodo_pago": "efectivo",
                "estado": "completada",
                "detalles": [
                    {"id_producto": 1, "cantidad": 1, "precio_unitario": 5.0}
                ],
            },
        )
        assert response.status_code == 400


class TestActualizarVenta:
    def test_actualizar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:venta|update|eq:id_venta:1": {"data": [_venta_data()]},
            "table:venta|select:*, cliente(*)|eq:id_venta:1": {
                "data": [{**_venta_data(), "observaciones": "Mod"}]
            },
            "table:detalle_venta|select:*, producto(*)|eq:id_venta:1": {"data": []},
        }
        override_db(mock_db)
        response = client.patch(
            "/api/ventas/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"observaciones": "Mod"},
        )
        assert response.status_code == 200
        assert response.json()["observaciones"] == "Mod"

    def test_actualizar_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {
            "table:venta|update|eq:id_venta:99": {"data": []}
        }
        override_db(mock_db)
        response = client.patch(
            "/api/ventas/99",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"observaciones": "Mod"},
        )
        assert response.status_code == 404


class TestCancelarVenta:
    def test_cancelar_exitoso(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {"rpc:cancelar_venta": {"data": [{"ok": True}]}}
        override_db(mock_db)
        response = client.delete(
            "/api/ventas/1", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "cancelada" in response.json()["mensaje"]

    def test_cancelar_no_encontrada(self, client, admin_token, override_db, mock_db):
        mock_db.responses = {"rpc:cancelar_venta": {"data": []}}
        override_db(mock_db)
        response = client.delete(
            "/api/ventas/99", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

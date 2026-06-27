"""Servicio de logica de negocio para Proveedores."""

from __future__ import annotations

from app.services.base_service import BaseCRUDService

_service = BaseCRUDService("proveedor", "id_proveedor")
listar = _service.listar
obtener = _service.obtener
crear = _service.crear
actualizar = _service.actualizar
eliminar = _service.eliminar

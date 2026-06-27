"""Servicio de logica de negocio para Clientes."""

from __future__ import annotations

from app.services.base_service import BaseCRUDService

_service = BaseCRUDService("cliente", "id_cliente")
listar = _service.listar
obtener = _service.obtener
crear = _service.crear
actualizar = _service.actualizar
eliminar = _service.eliminar

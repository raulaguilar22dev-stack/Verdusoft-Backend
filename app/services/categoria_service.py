"""Servicio de logica de negocio para Categorias."""

from __future__ import annotations

from postgrest.exceptions import APIError

from app.services.base_service import BaseCRUDService


def _handle_duplicate(e: APIError):
    if "duplicate" in str(e).lower():
        return ValueError("Ya existe una categoria con ese nombre")
    return None


_service = BaseCRUDService("categoria", "id_categoria", error_handler=_handle_duplicate)
listar = _service.listar
obtener = _service.obtener
crear = _service.crear
actualizar = _service.actualizar
eliminar = _service.eliminar

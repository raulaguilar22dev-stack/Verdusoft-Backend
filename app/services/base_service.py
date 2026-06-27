"""Servicio CRUD base generico para entidades maestras."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from postgrest.exceptions import APIError
from supabase import Client

logger = logging.getLogger(__name__)

ErrorHandler = Callable[[APIError], Optional[Exception]]


class BaseCRUDService:
    """CRUD generico con soft-delete para tablas maestras."""

    def __init__(
        self,
        tabla: str,
        id_column: str,
        orden: str = "nombre",
        error_handler: Optional[ErrorHandler] = None,
    ):
        self.tabla = tabla
        self.id_column = id_column
        self.orden = orden
        self.error_handler = error_handler

    def listar(
        self,
        db: Client,
        *,
        activo: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """Listar con paginacion y filtro de activo."""
        query = db.table(self.tabla).select("*")
        if activo is not None:
            query = query.eq("activo", activo)
        query = query.order(self.orden).range(skip, skip + limit - 1)
        response = query.execute()
        return response.data or []

    def obtener(self, db: Client, id_val: int) -> dict:
        """Obtener por ID."""
        response = (
            db.table(self.tabla).select("*").eq(self.id_column, id_val).execute()
        )
        if not response.data:
            raise ValueError(f"{self.tabla.title()} no encontrado/a")
        return response.data[0]

    def crear(self, db: Client, schema) -> dict:
        """Crear registro."""
        try:
            data = schema.model_dump(mode="json")
            response = db.table(self.tabla).insert(data).execute()
            return response.data[0]
        except APIError as e:
            logger.error(f"Error al crear en {self.tabla}: {e}")
            if self.error_handler:
                result = self.error_handler(e)
                if result:
                    raise result
            raise ValueError(f"Error al crear {self.tabla}")
        except Exception as e:
            logger.error(f"Error inesperado al crear en {self.tabla}: {e}")
            raise ValueError(f"Error al crear {self.tabla}")

    def actualizar(self, db: Client, id_val: int, schema) -> dict:
        """Actualizar parcialmente."""
        data = schema.model_dump(exclude_unset=True, mode="json")
        if not data:
            raise ValueError("No hay datos para actualizar")
        response = (
            db.table(self.tabla).update(data).eq(self.id_column, id_val).execute()
        )
        if not response.data:
            raise ValueError(f"{self.tabla.title()} no encontrado/a")
        return response.data[0]

    def eliminar(self, db: Client, id_val: int) -> dict:
        """Soft-delete."""
        response = (
            db.table(self.tabla)
            .update({"activo": False})
            .eq(self.id_column, id_val)
            .execute()
        )
        if not response.data:
            raise ValueError(f"{self.tabla.title()} no encontrado/a")
        return {"mensaje": f"{self.tabla.title()} desactivado/a exitosamente"}

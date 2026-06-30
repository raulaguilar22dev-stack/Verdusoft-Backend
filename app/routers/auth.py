"""Router de autenticacion: registro de admin y utilidades de auth."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Auth"])


class RegistroAdminRequest(BaseModel):
    email: EmailStr
    password: str
    master_key: str


class RegistroAdminResponse(BaseModel):
    mensaje: str
    user_id: str


@router.post("/auth/register", response_model=RegistroAdminResponse)
async def registrar_admin(data: RegistroAdminRequest):
    """Registra un nuevo usuario admin usando la clave maestra.

    Requiere la ADMIN_MASTER_KEY para evitar registros no autorizados.
    El usuario se crea en Supabase Auth con app_metadata.role = 'admin'.
    """
    if data.master_key != settings.admin_master_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave maestra incorrecta",
        )

    url = f"{settings.supabase_url}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {settings.supabase_key}",
        "Content-Type": "application/json",
        "apikey": settings.supabase_key,
    }
    payload = {
        "email": data.email,
        "password": data.password,
        "app_metadata": {"role": "admin"},
        "email_confirm": True,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as e:
            logger.error(f"Error de conexion con Supabase Auth: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error de conexion con el servicio de autenticacion",
            )

    if response.status_code == 422:
        detail = response.json().get("msg", "Datos invalidos")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    if response.status_code >= 400:
        logger.error(f"Error de Supabase Auth: {response.status_code} {response.text}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear usuario. El email ya existe o la contrasena es demasiado debil.",
        )

    user_data = response.json()
    user_id = user_data.get("id")

    return RegistroAdminResponse(
        mensaje="Usuario admin creado exitosamente",
        user_id=user_id,
    )

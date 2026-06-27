"""Dependencias de autenticacion para FastAPI."""

from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException, status

from app.auth.roles import UserRole


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Placeholder para extraccion de JWT.

    Por ahora permite paso libre. En Fase 4 se implementara
    validacion real contra Supabase Auth.
    """
    # TODO(Fase 4): Validar JWT con supabase-auth
    return {"role": UserRole.ADMIN, "id": None}


async def require_admin(user: dict = get_current_user) -> dict:
    """Requiere rol admin. Placeholder."""
    # TODO(Fase 4): Verificar user["role"] == UserRole.ADMIN
    return user

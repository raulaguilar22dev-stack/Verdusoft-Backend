"""Dependencias de autenticacion para FastAPI."""

from __future__ import annotations

import logging
from typing import Optional

import jwt
from fastapi import Header, HTTPException, status

from app.auth.roles import UserRole
from app.config import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Valida el JWT de Supabase Auth y extrae el usuario."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el header Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization invalido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[ALGORITHM],
            options={"verify_aud": False},
            leeway=60,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token invalido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    app_metadata = payload.get("app_metadata", {})
    user_role = app_metadata.get("role", UserRole.PUBLIC.value)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user_id,
        "role": user_role,
        "email": payload.get("email"),
    }


async def require_admin(
    authorization: Optional[str] = Header(None),
) -> dict:
    """Requiere que el usuario autenticado tenga rol admin."""
    user = await get_current_user(authorization)

    if user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de administrador",
        )

    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """Valida el JWT si existe, sino devuelve None (para endpoints publicos)."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None

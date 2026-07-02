"""Dependencias de autenticacion para FastAPI."""

from __future__ import annotations

import logging
from typing import Optional

import jwt
from fastapi import Header, HTTPException, status

from app.auth.roles import UserRole
from app.config import settings

logger = logging.getLogger(__name__)

# Cache del cliente JWKS para RS256 (Supabase Auth v2 default)
_jwks_client = None


def _get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"https://{settings.supabase_project_ref}.supabase.co/auth/v1/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_url)
    return _jwks_client


def _decode_token(token: str) -> dict:
    """Decodifica un JWT de Supabase Auth, soportando RS256 (default) y HS256 (legacy)."""
    unverified_header = jwt.get_unverified_header(token)
    alg = unverified_header.get("alg", "RS256")

    if alg == "RS256":
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            leeway=300,
        )
    elif alg == "HS256":
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
            leeway=300,
        )
    else:
        raise jwt.InvalidTokenError(f"Algoritmo JWT no soportado: {alg}")


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
        payload = _decode_token(token)
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

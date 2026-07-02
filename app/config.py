"""Configuración de la aplicación cargada desde variables de entorno."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global del backend."""

    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    supabase_project_ref: str = "lscmcxxvayzdgwinpokx"
    admin_master_key: str = "verdusoft-admin-2026"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

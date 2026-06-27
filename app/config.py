"""Configuración de la aplicación cargada desde variables de entorno."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global del backend."""

    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

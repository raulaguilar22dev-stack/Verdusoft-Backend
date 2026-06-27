"""Cliente de base de datos Supabase (singleton)."""

from supabase import create_client, Client

from app.config import settings

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Retorna la instancia única del cliente Supabase."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client

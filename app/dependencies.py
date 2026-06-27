"""Dependencias inyectables para FastAPI."""

from fastapi import Depends
from supabase import Client

from app.database import get_supabase


def get_supabase_client() -> Client:
    """Dependencia que provee el cliente Supabase a los routers."""
    return get_supabase()

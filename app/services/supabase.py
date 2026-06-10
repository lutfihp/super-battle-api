from supabase import create_client, Client
from app.config import get_settings

_client: Client | None = None


def get_supabase_client() -> Client | None:
    global _client
    if _client is not None:
        return _client
    settings = get_settings()
    if not settings.supabase_url:
        return None
    key = settings.supabase_service_key or settings.supabase_anon_key
    if not key:
        return None
    _client = create_client(settings.supabase_url, key)
    return _client

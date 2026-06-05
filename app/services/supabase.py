from app.config import get_settings


def get_supabase_client():
    """
    Returns a configured Supabase client, or None if credentials are not set.
    In stub mode (no env vars), returns None — callers must guard against this.
    Uncomment the real implementation when wiring up real data in the integration phase.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        return None
    # Integration phase — uncomment and add `supabase>=2.10.0` to requirements.txt:
    # from supabase import create_client
    # return create_client(settings.supabase_url, settings.supabase_anon_key)
    return None

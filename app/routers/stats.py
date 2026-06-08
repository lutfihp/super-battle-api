from fastapi import APIRouter

from app.models import StatsResponse
from app.services.supabase import get_supabase_client

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def get_stats():
    db = get_supabase_client()
    if db is None:
        return StatsResponse(battles_cached=0, characters_loaded=0)

    char_result = db.table("characters").select("*", count="exact").execute()
    battle_result = db.table("battles").select("*", count="exact").execute()

    return StatsResponse(
        battles_cached=battle_result.count or 0,
        characters_loaded=char_result.count or 0,
    )

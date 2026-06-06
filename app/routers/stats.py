from fastapi import APIRouter

from app.models import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def get_stats():
    return StatsResponse(battles_cached=2847, characters_loaded=203)

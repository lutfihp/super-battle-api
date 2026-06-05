from fastapi import APIRouter

from app.models import BattleRequest, BattleResponse
from app.services.battle import run_battle_stub

router = APIRouter()


@router.post("/battle", response_model=BattleResponse)
def battle(request: BattleRequest):
    return run_battle_stub()

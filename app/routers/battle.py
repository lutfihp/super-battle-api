from fastapi import APIRouter, HTTPException

from app.models import BattleRequest, BattleResponse
from app.services.characters import get_characters_by_ids
from app.services.battle import run_battle

router = APIRouter()


@router.post("/battle", response_model=BattleResponse)
def battle(request: BattleRequest):
    all_ids = request.team_a + request.team_b
    characters = get_characters_by_ids(all_ids)
    char_map = {c.id: c for c in characters}

    for id_ in all_ids:
        if id_ not in char_map:
            raise HTTPException(status_code=404, detail=f"Character {id_} not found")

    team_a = [char_map[i] for i in request.team_a]
    team_b = [char_map[i] for i in request.team_b]
    return run_battle(team_a, team_b)

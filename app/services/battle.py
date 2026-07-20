from app.models import Character, BattleResponse
from app.services.supabase import get_supabase_client
from app.services.fireworks_service import generate_battle_story


TEAM_MULTIPLIERS = {1: 1.0, 2: 0.6, 3: 0.5}


def compute_score(characters: list[Character]) -> int:
    stats = ["intelligence", "strength", "speed", "durability", "power", "combat"]
    raw = sum(getattr(c, s, 0) or 0 for c in characters for s in stats)
    multiplier = TEAM_MULTIPLIERS.get(len(characters), 0.5)
    return round(raw * multiplier)


def make_matchup_key(a_ids: list[str], b_ids: list[str]) -> str:
    a = "-".join(sorted(a_ids))
    b = "-".join(sorted(b_ids))
    parts = sorted([a, b])
    return f"{parts[0]}_vs_{parts[1]}"


def run_battle(
    team_a: list[Character], team_b: list[Character]
) -> BattleResponse:
    db = get_supabase_client()
    key = make_matchup_key([c.id for c in team_a], [c.id for c in team_b])

    if db is not None:
        cached = db.table("battles").select("*").eq("matchup_key", key).execute()
        if cached.data:
            row = cached.data[0]
            return BattleResponse(
                story=row["story"],
                winner=row["winner"],
                score_a=row["score_a"],
                score_b=row["score_b"],
                team_a=team_a,
                team_b=team_b,
                cached=True,
            )

    score_a = compute_score(team_a)
    score_b = compute_score(team_b)
    winner = "A" if score_a >= score_b else "B"
    story = generate_battle_story(team_a, team_b, winner)

    if db is not None:
        db.table("battles").insert({
            "matchup_key": key,
            "story": story,
            "winner": winner,
            "score_a": score_a,
            "score_b": score_b,
        }).execute()

    return BattleResponse(
        story=story,
        winner=winner,
        score_a=score_a,
        score_b=score_b,
        team_a=team_a,
        team_b=team_b,
        cached=False,
    )

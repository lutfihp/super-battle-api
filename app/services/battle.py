from app.models import Character, BattleResponse

STUB_STORY = [
    "The battle begins as Batman and Superman charge forward with calculated fury.",
    "Wonder Woman deflects the assault while Joker unleashes chemical chaos.",
    "Batman's tactical genius opens a gap in the villain line — Team A presses the advantage.",
    "Joker's unpredictable strike catches Superman off-guard, rattling the heroes.",
    "The flash of Superman's heat vision scorches the battlefield, turning the tide.",
    "Wonder Woman rallies, her lasso binding two heroes — Team B surges with renewed hope.",
    "A single, decisive strike from Batman ends the stalemate — the heroes seize the moment.",
    "The smoke clears: Team A stands victorious, their combined power undeniable.",
]


def compute_score(characters: list[Character]) -> int:
    stats = ["intelligence", "strength", "speed", "durability", "power", "combat"]
    return sum(getattr(c, s, 0) or 0 for c in characters for s in stats)


def make_matchup_key(a_ids: list[str], b_ids: list[str]) -> str:
    a = "-".join(sorted(a_ids))
    b = "-".join(sorted(b_ids))
    parts = sorted([a, b])
    return f"{parts[0]}_vs_{parts[1]}"


def run_battle_stub() -> BattleResponse:
    from app.services.characters import STUB_CHARACTERS

    team_a = STUB_CHARACTERS[:2]   # Batman (335), Superman (579) → 914
    team_b = STUB_CHARACTERS[2:]   # Joker (221), Wonder Woman (528) → 749

    score_a = compute_score(team_a)
    score_b = compute_score(team_b)
    winner = "A" if score_a >= score_b else "B"

    return BattleResponse(
        story=STUB_STORY,
        winner=winner,
        score_a=score_a,
        score_b=score_b,
        team_a=team_a,
        team_b=team_b,
    )

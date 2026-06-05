from app.models import Character


def compute_score(characters: list[Character]) -> int:
    stats = ["intelligence", "strength", "speed", "durability", "power", "combat"]
    return sum(getattr(c, s, 0) or 0 for c in characters for s in stats)


def make_matchup_key(a_ids: list[str], b_ids: list[str]) -> str:
    a = "-".join(sorted(a_ids))
    b = "-".join(sorted(b_ids))
    parts = sorted([a, b])
    return f"{parts[0]}_vs_{parts[1]}"

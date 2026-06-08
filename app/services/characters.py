from app.models import Character
from app.services.supabase import get_supabase_client


def rows_to_characters(rows: list[dict]) -> list[Character]:
    return [
        Character(
            id=str(row["id"]),
            name=row["name"],
            alignment=row.get("alignment") or "good",
            image_url=row.get("image_url") or "",
            intelligence=row.get("intelligence") or 0,
            strength=row.get("strength") or 0,
            speed=row.get("speed") or 0,
            durability=row.get("durability") or 0,
            power=row.get("power") or 0,
            combat=row.get("combat") or 0,
            powers_text=row.get("description") or "",
            description=row.get("description"),
        )
        for row in rows
    ]


POPULAR_IDS = [
    # Marvel Heroes
    620, 346, 149, 717,
    # Marvel Villains
    655, 222, 423, 299,
    # DC Heroes
    70, 720, 263, 38,
    # DC Villains
    204, 405, 309, 60,
]


def get_popular_characters() -> list[Character]:
    db = get_supabase_client()
    if db is None:
        return []
    result = (
        db.table("characters")
        .select("*")
        .in_("id", POPULAR_IDS)
        .execute()
    )
    return rows_to_characters(result.data)


def search_characters(q: str) -> list[Character]:
    db = get_supabase_client()
    if db is None:
        return []
    result = (
        db.table("characters")
        .select("*")
        .ilike("name", f"%{q}%")
        .limit(20)
        .execute()
    )
    return rows_to_characters(result.data)


def get_characters_by_ids(ids: list[str]) -> list[Character]:
    db = get_supabase_client()
    if db is None:
        return []
    int_ids = [int(i) for i in ids]
    result = (
        db.table("characters")
        .select("*")
        .in_("id", int_ids)
        .execute()
    )
    return rows_to_characters(result.data)

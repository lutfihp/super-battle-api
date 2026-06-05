from app.models import Character

STUB_CHARACTERS: list[Character] = [
    Character(
        id="70",
        name="Batman",
        alignment="good",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/70.jpg",
        intelligence=100,
        strength=26,
        speed=27,
        durability=47,
        power=35,
        combat=100,
        powers_text="Martial Arts, Stealth, Gadgetry, Detective Genius",
    ),
    Character(
        id="644",
        name="Superman",
        alignment="good",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/644.jpg",
        intelligence=94,
        strength=100,
        speed=100,
        durability=100,
        power=100,
        combat=85,
        powers_text="Flight, Super Strength, Heat Vision, Invulnerability, Super Speed",
    ),
    Character(
        id="370",
        name="Joker",
        alignment="bad",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/370.jpg",
        intelligence=90,
        strength=10,
        speed=12,
        durability=32,
        power=35,
        combat=42,
        powers_text="Unpredictability, Toxin Immunity, Genius-level Intellect, Chemical Weapons",
    ),
    Character(
        id="720",
        name="Wonder Woman",
        alignment="good",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/720.jpg",
        intelligence=88,
        strength=100,
        speed=79,
        durability=80,
        power=80,
        combat=101,
        powers_text="Super Strength, Flight, Lasso of Truth, Combat Mastery, Godlike Durability",
    ),
]


def get_popular_characters() -> list[Character]:
    return STUB_CHARACTERS


def search_characters(q: str) -> list[Character]:
    q_lower = q.lower()
    return [c for c in STUB_CHARACTERS if q_lower in c.name.lower()]

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Character, BattleResponse

STUB_CHARACTERS = [
    Character(
        id="70", name="Batman", alignment="good",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/70.jpg",
        intelligence=100, strength=26, speed=27, durability=47, power=35, combat=100,
        powers_text="Martial Arts, Stealth, Gadgetry, Detective Genius",
    ),
    Character(
        id="644", name="Superman", alignment="good",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/644.jpg",
        intelligence=94, strength=100, speed=100, durability=100, power=100, combat=85,
        powers_text="Flight, Super Strength, Heat Vision, Invulnerability, Super Speed",
    ),
    Character(
        id="370", name="Joker", alignment="bad",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/370.jpg",
        intelligence=90, strength=10, speed=12, durability=32, power=35, combat=42,
        powers_text="Unpredictability, Toxin Immunity, Genius-level Intellect, Chemical Weapons",
    ),
    Character(
        id="720", name="Wonder Woman", alignment="good",
        image_url="https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/images/sm/720.jpg",
        intelligence=88, strength=100, speed=79, durability=80, power=80, combat=101,
        powers_text="Super Strength, Flight, Lasso of Truth, Combat Mastery, Godlike Durability",
    ),
]

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

STUB_BATTLE = BattleResponse(
    story=STUB_STORY,
    winner="A",
    score_a=914,
    score_b=749,
    team_a=STUB_CHARACTERS[:2],
    team_b=STUB_CHARACTERS[2:],
    cached=False,
)


@pytest.fixture(autouse=True)
def mock_services(mocker):
    mocker.patch(
        "app.routers.characters.get_popular_characters",
        return_value=STUB_CHARACTERS,
    )
    mocker.patch(
        "app.routers.characters.search_characters",
        side_effect=lambda q: [c for c in STUB_CHARACTERS if q.lower() in c.name.lower()],
    )
    mocker.patch(
        "app.routers.battle.get_characters_by_ids",
        side_effect=lambda ids: [c for c in STUB_CHARACTERS if c.id in ids],
    )
    mocker.patch(
        "app.routers.battle.run_battle",
        return_value=STUB_BATTLE,
    )
    stats_db = mocker.MagicMock()
    stats_db.table.return_value.select.return_value.execute.return_value.count = 4
    mocker.patch("app.routers.stats.get_supabase_client", return_value=stats_db)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

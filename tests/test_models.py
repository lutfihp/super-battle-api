import pytest
from pydantic import ValidationError
from app.models import Character, BattleRequest, BattleResponse, HealthResponse


def _make_character(**overrides) -> dict:
    base = dict(
        id="70", name="Batman", alignment="good",
        image_url="https://example.com/img.jpg",
        intelligence=100, strength=26, speed=27,
        durability=47, power=35, combat=100,
        powers_text="Martial Arts",
    )
    base.update(overrides)
    return base


def test_character_model_accepts_valid_data():
    char = Character(**_make_character())
    assert char.name == "Batman"
    assert char.alignment == "good"
    assert char.intelligence == 100


def test_character_model_rejects_missing_field():
    with pytest.raises(ValidationError):
        Character(**_make_character(name=None))


def test_battle_request_valid():
    req = BattleRequest(team_a=["70", "644"], team_b=["370", "720"])
    assert req.team_a == ["70", "644"]
    assert req.team_b == ["370", "720"]


def test_battle_request_rejects_missing_field():
    with pytest.raises(ValidationError):
        BattleRequest(team_a=["1"])


def test_battle_response_valid():
    char = Character(**_make_character())
    resp = BattleResponse(
        story=["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"],
        winner="A",
        score_a=914,
        score_b=749,
        team_a=[char],
        team_b=[char],
    )
    assert len(resp.story) == 8
    assert resp.winner == "A"


def test_health_response_valid():
    h = HealthResponse(status="ok")
    assert h.status == "ok"

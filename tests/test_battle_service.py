from unittest.mock import MagicMock
from app.models import Character, BattleResponse

_STORY = [f"Sentence {i}." for i in range(1, 9)]


def _char(id_, name, score=100):
    per_stat = score // 6
    return Character(
        id=id_, name=name, alignment="good", image_url="",
        intelligence=per_stat, strength=per_stat, speed=per_stat,
        durability=per_stat, power=per_stat, combat=per_stat,
        powers_text="",
    )


def _make_battles_db(cached_row=None):
    db = MagicMock()
    cached = [cached_row] if cached_row else []
    db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = cached
    db.table.return_value.insert.return_value.execute.return_value.data = [{}]
    return db


def test_run_battle_returns_response(mocker):
    mocker.patch("app.services.battle.get_supabase_client", return_value=_make_battles_db())
    mocker.patch("app.services.battle.generate_battle_story", return_value=_STORY)
    from app.services.battle import run_battle
    result = run_battle([_char("1", "Hero")], [_char("2", "Villain")])
    assert isinstance(result, BattleResponse)
    assert len(result.story) == 8
    assert result.cached is False


def test_run_battle_returns_cached_result(mocker):
    cached = {
        "matchup_key": "1_vs_2",
        "story": _STORY,
        "winner": "A",
        "score_a": 100,
        "score_b": 80,
    }
    mocker.patch("app.services.battle.get_supabase_client", return_value=_make_battles_db(cached))
    mock_groq = mocker.patch("app.services.battle.generate_battle_story")
    from app.services.battle import run_battle
    result = run_battle([_char("1", "Hero")], [_char("2", "Villain")])
    assert result.cached is True
    mock_groq.assert_not_called()


def test_run_battle_writes_to_cache(mocker):
    db = _make_battles_db()
    mocker.patch("app.services.battle.get_supabase_client", return_value=db)
    mocker.patch("app.services.battle.generate_battle_story", return_value=_STORY)
    from app.services.battle import run_battle
    run_battle([_char("1", "Hero")], [_char("2", "Villain")])
    db.table.return_value.insert.return_value.execute.assert_called_once()

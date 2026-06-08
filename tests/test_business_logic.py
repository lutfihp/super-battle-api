from app.models import Character
from app.services.battle import compute_score, make_matchup_key


def _char(**overrides) -> Character:
    base = dict(
        id="1", name="Test", alignment="good",
        image_url="https://example.com/img.jpg",
        intelligence=10, strength=10, speed=10,
        durability=10, power=10, combat=10,
        powers_text="",
    )
    base.update(overrides)
    return Character(**base)


def test_compute_score_sums_six_stats():
    char = _char(intelligence=10, strength=20, speed=30,
                 durability=40, power=50, combat=60)
    assert compute_score([char]) == 210


def test_compute_score_multiple_characters():
    c1 = _char(intelligence=10, strength=10, speed=10,
               durability=10, power=10, combat=10)
    c2 = _char(intelligence=20, strength=20, speed=20,
               durability=20, power=20, combat=20)
    assert compute_score([c1, c2]) == 108  # raw 180 × 0.6


def test_compute_score_empty_list():
    assert compute_score([]) == 0


def test_compute_score_known_stub_values():
    # Batman: 100+26+27+47+35+100 = 335
    batman = _char(intelligence=100, strength=26, speed=27,
                   durability=47, power=35, combat=100)
    assert compute_score([batman]) == 335


def test_matchup_key_is_order_independent():
    key1 = make_matchup_key(["70", "644"], ["370", "720"])
    key2 = make_matchup_key(["370", "720"], ["70", "644"])
    assert key1 == key2


def test_matchup_key_sorts_ids_within_team():
    key1 = make_matchup_key(["644", "70"], ["720", "370"])
    key2 = make_matchup_key(["70", "644"], ["370", "720"])
    assert key1 == key2


def test_matchup_key_format():
    key = make_matchup_key(["70"], ["370"])
    assert "_vs_" in key


def test_compute_score_1char_multiplier_is_1():
    char = _char(intelligence=10, strength=10, speed=10,
                 durability=10, power=10, combat=10)
    assert compute_score([char]) == 60  # raw 60 × 1.0


def test_compute_score_2char_multiplier_is_0_6():
    c1 = _char(intelligence=10, strength=10, speed=10,
               durability=10, power=10, combat=10)
    c2 = _char(id="2", intelligence=10, strength=10, speed=10,
               durability=10, power=10, combat=10)
    assert compute_score([c1, c2]) == 72  # raw 120 × 0.6


def test_compute_score_3char_multiplier_is_0_5():
    c1 = _char(intelligence=10, strength=10, speed=10,
               durability=10, power=10, combat=10)
    c2 = _char(id="2", intelligence=10, strength=10, speed=10,
               durability=10, power=10, combat=10)
    c3 = _char(id="3", intelligence=10, strength=10, speed=10,
               durability=10, power=10, combat=10)
    assert compute_score([c1, c2, c3]) == 90  # raw 180 × 0.5

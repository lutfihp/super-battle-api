from unittest.mock import MagicMock

ROW = {
    "id": 70, "name": "Batman", "alignment": "good",
    "image_url": "https://example.com/img.jpg",
    "intelligence": 100, "strength": 26, "speed": 27,
    "durability": 47, "power": 35, "combat": 100,
    "description": "The Dark Knight.", "publisher": "DC Comics",
}


def _make_db(rows):
    db = MagicMock()
    db.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = rows
    db.table.return_value.select.return_value.ilike.return_value.limit.return_value.execute.return_value.data = rows
    db.table.return_value.select.return_value.in_.return_value.execute.return_value.data = rows
    return db


def test_get_popular_returns_characters(mocker):
    mocker.patch("app.services.characters.get_supabase_client", return_value=_make_db([ROW]))
    from app.services.characters import get_popular_characters
    result = get_popular_characters()
    assert len(result) == 1
    assert result[0].name == "Batman"
    assert result[0].id == "70"


def test_get_popular_returns_empty_when_no_client(mocker):
    mocker.patch("app.services.characters.get_supabase_client", return_value=None)
    from app.services.characters import get_popular_characters
    assert get_popular_characters() == []


def test_search_returns_characters(mocker):
    mocker.patch("app.services.characters.get_supabase_client", return_value=_make_db([ROW]))
    from app.services.characters import search_characters
    result = search_characters("bat")
    assert result[0].name == "Batman"


def test_get_characters_by_ids_returns_characters(mocker):
    mocker.patch("app.services.characters.get_supabase_client", return_value=_make_db([ROW]))
    from app.services.characters import get_characters_by_ids
    result = get_characters_by_ids(["70"])
    assert result[0].id == "70"


def test_rows_to_characters_maps_description_to_powers_text():
    from app.services.characters import rows_to_characters
    chars = rows_to_characters([ROW])
    assert chars[0].powers_text == "The Dark Knight."
    assert chars[0].description == "The Dark Knight."

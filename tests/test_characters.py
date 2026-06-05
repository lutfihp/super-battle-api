REQUIRED_FIELDS = {
    "id", "name", "alignment", "image_url",
    "intelligence", "strength", "speed",
    "durability", "power", "combat", "powers_text",
}


def test_popular_returns_list_of_characters(client):
    response = client.get("/api/characters/popular")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_popular_characters_have_required_fields(client):
    response = client.get("/api/characters/popular")
    data = response.json()
    for char in data:
        assert REQUIRED_FIELDS.issubset(char.keys()), f"Missing fields in {char['name']}"


def test_search_finds_batman(client):
    response = client.get("/api/characters/search?q=bat")
    assert response.status_code == 200
    data = response.json()
    names = [c["name"] for c in data]
    assert "Batman" in names


def test_search_case_insensitive(client):
    response = client.get("/api/characters/search?q=BATMAN")
    assert response.status_code == 200
    data = response.json()
    assert any(c["name"] == "Batman" for c in data)


def test_search_no_results_returns_empty_list(client):
    response = client.get("/api/characters/search?q=zzznomatch")
    assert response.status_code == 200
    assert response.json() == []


def test_search_missing_q_returns_422(client):
    response = client.get("/api/characters/search")
    assert response.status_code == 422

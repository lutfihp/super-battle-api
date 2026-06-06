def test_stats_returns_200(client):
    response = client.get("/api/stats")
    assert response.status_code == 200


def test_stats_has_required_integer_fields(client):
    response = client.get("/api/stats")
    data = response.json()
    assert isinstance(data["battles_cached"], int)
    assert isinstance(data["characters_loaded"], int)


def test_stats_values_are_positive(client):
    response = client.get("/api/stats")
    data = response.json()
    assert data["battles_cached"] >= 0
    assert data["characters_loaded"] >= 0

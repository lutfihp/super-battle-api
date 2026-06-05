VALID_PAYLOAD = {"team_a": ["70", "644"], "team_b": ["370", "720"]}


def test_battle_valid_request_returns_200(client):
    response = client.post("/api/battle", json=VALID_PAYLOAD)
    assert response.status_code == 200


def test_battle_response_has_eight_story_sentences(client):
    response = client.post("/api/battle", json=VALID_PAYLOAD)
    data = response.json()
    assert len(data["story"]) == 8


def test_battle_response_winner_is_valid(client):
    response = client.post("/api/battle", json=VALID_PAYLOAD)
    data = response.json()
    assert data["winner"] in ("A", "B", "tie")


def test_battle_response_scores_are_integers(client):
    response = client.post("/api/battle", json=VALID_PAYLOAD)
    data = response.json()
    assert isinstance(data["score_a"], int)
    assert isinstance(data["score_b"], int)


def test_battle_response_has_team_character_lists(client):
    response = client.post("/api/battle", json=VALID_PAYLOAD)
    data = response.json()
    assert isinstance(data["team_a"], list)
    assert isinstance(data["team_b"], list)


def test_battle_stub_score_a_beats_score_b(client):
    # Batman (335) + Superman (579) = 914 vs Joker (221) + Wonder Woman (528) = 749
    response = client.post("/api/battle", json=VALID_PAYLOAD)
    data = response.json()
    assert data["score_a"] == 914
    assert data["score_b"] == 749
    assert data["winner"] == "A"


def test_battle_malformed_body_returns_422(client):
    response = client.post("/api/battle", json={"bad_field": "value"})
    assert response.status_code == 422


def test_battle_missing_body_returns_422(client):
    response = client.post("/api/battle")
    assert response.status_code == 422

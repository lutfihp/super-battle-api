from app.models import Character


def _char():
    return Character(
        id="1", name="X", alignment="good", image_url="",
        intelligence=10, strength=10, speed=10,
        durability=10, power=10, combat=10, powers_text="",
    )


def test_generate_battle_story_returns_eight_sentences(mocker):
    fake_content = "\n".join([f"Sentence {i}." for i in range(1, 9)])
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = fake_content
    mock_groq_client = mocker.MagicMock()
    mock_groq_client.chat.completions.create.return_value = mock_response
    mocker.patch("app.services.groq_service.Groq", return_value=mock_groq_client)
    mocker.patch(
        "app.services.groq_service.get_settings",
        return_value=mocker.MagicMock(groq_api_key="test-key"),
    )
    from app.services.groq_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8
    assert all(isinstance(s, str) for s in result)


def test_generate_battle_story_pads_short_response(mocker):
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = "Only one sentence."
    mock_groq_client = mocker.MagicMock()
    mock_groq_client.chat.completions.create.return_value = mock_response
    mocker.patch("app.services.groq_service.Groq", return_value=mock_groq_client)
    mocker.patch(
        "app.services.groq_service.get_settings",
        return_value=mocker.MagicMock(groq_api_key="test-key"),
    )
    from app.services.groq_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8


def test_generate_battle_story_trims_long_response(mocker):
    fake_content = "\n".join([f"Sentence {i}." for i in range(1, 15)])
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = fake_content
    mock_groq_client = mocker.MagicMock()
    mock_groq_client.chat.completions.create.return_value = mock_response
    mocker.patch("app.services.groq_service.Groq", return_value=mock_groq_client)
    mocker.patch(
        "app.services.groq_service.get_settings",
        return_value=mocker.MagicMock(groq_api_key="test-key"),
    )
    from app.services.groq_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8

from app.models import Character


def _char():
    return Character(
        id="1", name="X", alignment="good", image_url="",
        intelligence=10, strength=10, speed=10,
        durability=10, power=10, combat=10, powers_text="",
    )


def _mock_client(mocker, content):
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = content
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mocker.patch("app.services.fireworks_service.OpenAI", return_value=mock_client)
    mocker.patch(
        "app.services.fireworks_service.get_settings",
        return_value=mocker.MagicMock(fireworks_api_key="test-key"),
    )


def test_generate_battle_story_returns_eight_sentences(mocker):
    _mock_client(mocker, "\n".join(f"Sentence {i}." for i in range(1, 9)))
    from app.services.fireworks_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8
    assert all(isinstance(s, str) for s in result)


def test_generate_battle_story_pads_short_response(mocker):
    _mock_client(mocker, "Only one sentence.")
    from app.services.fireworks_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8


def test_generate_battle_story_trims_long_response(mocker):
    _mock_client(mocker, "\n".join(f"Sentence {i}." for i in range(1, 15)))
    from app.services.fireworks_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8


def test_generate_battle_story_splits_single_paragraph(mocker):
    # gpt-oss-120b often returns all sentences as one paragraph, no newlines.
    # The parser must sentence-split on punctuation, not just newlines.
    paragraph = " ".join(f"Sentence number {i}." for i in range(1, 9))
    _mock_client(mocker, paragraph)
    from app.services.fireworks_service import generate_battle_story
    result = generate_battle_story([_char()], [_char()])
    assert len(result) == 8
    assert result[0] == "Sentence number 1."
    assert result[7] == "Sentence number 8."
    assert _FILLER_UNUSED not in result


_FILLER_UNUSED = "The battle rages on with neither side yielding."

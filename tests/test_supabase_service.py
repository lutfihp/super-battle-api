import app.services.supabase as svc


def test_returns_none_without_credentials(mocker):
    mocker.patch.object(svc, "_client", None)
    mocker.patch("app.services.supabase.get_settings", return_value=mocker.MagicMock(
        supabase_url="", supabase_anon_key=""
    ))
    result = svc.get_supabase_client()
    assert result is None


def test_returns_client_with_credentials(mocker):
    mocker.patch.object(svc, "_client", None)
    mocker.patch("app.services.supabase.get_settings", return_value=mocker.MagicMock(
        supabase_url="https://test.supabase.co",
        supabase_anon_key="test-key",
    ))
    mock_create = mocker.patch("app.services.supabase.create_client", return_value="mock-client")
    result = svc.get_supabase_client()
    assert result == "mock-client"
    mock_create.assert_called_once_with("https://test.supabase.co", "test-key")


def test_singleton_not_recreated(mocker):
    sentinel = object()
    mocker.patch.object(svc, "_client", sentinel)
    result = svc.get_supabase_client()
    assert result is sentinel

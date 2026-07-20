from app.config import Settings, get_settings


def test_settings_has_correct_defaults():
    # Use _env_file=None to skip loading .env so we test actual default values
    settings = Settings(_env_file=None)
    assert settings.frontend_url == "http://localhost:3000"
    assert settings.superhero_api_key == ""
    assert settings.fireworks_api_key == ""
    assert settings.supabase_url == ""
    assert settings.supabase_anon_key == ""
    assert settings.comicvine_api_key == ""


def test_get_settings_returns_settings_instance():
    settings = get_settings()
    assert isinstance(settings, Settings)

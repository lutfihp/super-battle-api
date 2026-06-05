from app.config import Settings, get_settings


def test_settings_has_correct_defaults():
    settings = Settings()
    assert settings.frontend_url == "http://localhost:3000"
    assert settings.superhero_api_key == ""
    assert settings.groq_api_key == ""
    assert settings.supabase_url == ""
    assert settings.supabase_anon_key == ""
    assert settings.comicvine_api_key == ""


def test_get_settings_returns_settings_instance():
    settings = get_settings()
    assert isinstance(settings, Settings)

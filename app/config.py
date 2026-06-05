from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    superhero_api_key: str = ""
    comicvine_api_key: str = ""
    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

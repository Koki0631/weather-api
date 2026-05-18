from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    request_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> Settings:
    return Settings()

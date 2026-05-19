from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    open_meteo_geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1"
    open_meteo_forecast_base_url: str = "https://api.open-meteo.com/v1"
    request_timeout_seconds: float = 10.0
    database_url: str = "mysql+pymysql://weather:weather@localhost:3306/weather"
    database_enabled: bool = True
    secret_key: str = "dev-only-set-secret-key-in-env"


@lru_cache
def get_settings() -> Settings:
    return Settings()

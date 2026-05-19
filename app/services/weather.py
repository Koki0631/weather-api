import logging
from dataclasses import dataclass

import httpx

from app.config import Settings
from app.models.weather import WeatherRecord
from app.repositories.weather_repository import WeatherRepository
from app.schemas import WeatherHistoryItem, WeatherHistoryResponse, WeatherResponse

logger = logging.getLogger(__name__)

WMO_WEATHER_DESCRIPTIONS: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


class CityNotFoundError(Exception):
    pass


class UpstreamWeatherError(Exception):
    pass


class DatabaseUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class WeatherService:
    settings: Settings
    client: httpx.AsyncClient
    repository: WeatherRepository | None = None

    async def get_weather(self, city: str, user_id: int) -> WeatherResponse:
        latitude, longitude = await self._resolve_coordinates(city)
        weather = await self._fetch_current_weather(
            city=city, latitude=latitude, longitude=longitude
        )
        self._persist_weather(weather, user_id=user_id)
        return weather

    def get_weather_history(
        self, city: str, user_id: int, limit: int = 10
    ) -> WeatherHistoryResponse:
        if self.repository is None:
            raise DatabaseUnavailableError("Database is not available")

        records = self.repository.list_by_city_and_user(
            city=city, user_id=user_id, limit=limit
        )
        return WeatherHistoryResponse(
            city=city,
            user_id=user_id,
            items=[_record_to_history_item(record) for record in records],
        )

    def _persist_weather(self, weather: WeatherResponse, *, user_id: int) -> None:
        if self.repository is None:
            return

        try:
            self.repository.save_weather(
                city=weather.city,
                temperature_celsius=weather.temperature_celsius,
                description=weather.description,
                humidity=weather.humidity,
                wind_speed_mps=weather.wind_speed_mps,
                user_id=user_id,
            )
        except Exception:
            logger.exception(
                "Failed to persist weather for city=%s user_id=%s; continuing without DB",
                weather.city,
                user_id,
            )

    async def _resolve_coordinates(self, city: str) -> tuple[float, float]:
        url = f"{self.settings.open_meteo_geocoding_base_url}/search"
        params = {"name": city, "count": 1, "language": "en", "format": "json"}

        try:
            response = await self.client.get(
                url,
                params=params,
                timeout=self.settings.request_timeout_seconds,
            )
        except httpx.RequestError as exc:
            raise UpstreamWeatherError("Failed to reach geocoding provider") from exc

        if response.status_code != 200:
            raise UpstreamWeatherError(
                f"Geocoding provider returned status {response.status_code}"
            )

        results = response.json().get("results") or []
        if not results:
            raise CityNotFoundError(f"City not found: {city}")

        location = results[0]
        return float(location["latitude"]), float(location["longitude"])

    async def _fetch_current_weather(
        self,
        *,
        city: str,
        latitude: float,
        longitude: float,
    ) -> WeatherResponse:
        url = f"{self.settings.open_meteo_forecast_base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            ),
            "wind_speed_unit": "ms",
        }

        try:
            response = await self.client.get(
                url,
                params=params,
                timeout=self.settings.request_timeout_seconds,
            )
        except httpx.RequestError as exc:
            raise UpstreamWeatherError("Failed to reach weather provider") from exc

        if response.status_code != 200:
            raise UpstreamWeatherError(
                f"Weather provider returned status {response.status_code}"
            )

        current = response.json().get("current") or {}
        weather_code = int(current.get("weather_code", -1))
        description = WMO_WEATHER_DESCRIPTIONS.get(weather_code, "unknown")

        return WeatherResponse(
            city=city,
            temperature_celsius=float(current["temperature_2m"]),
            description=description,
            humidity=int(current["relative_humidity_2m"]),
            wind_speed_mps=float(current["wind_speed_10m"]),
        )


def _record_to_history_item(record: WeatherRecord) -> WeatherHistoryItem:
    return WeatherHistoryItem(
        id=record.id,
        city=record.city,
        temperature_celsius=record.temperature_celsius,
        description=record.description,
        humidity=record.humidity,
        wind_speed_mps=record.wind_speed_mps,
        created_at=record.created_at,
    )

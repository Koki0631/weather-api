from dataclasses import dataclass

import httpx

from app.config import Settings
from app.schemas import WeatherResponse


class CityNotFoundError(Exception):
    pass


class UpstreamWeatherError(Exception):
    pass


@dataclass(frozen=True)
class WeatherService:
    settings: Settings
    client: httpx.AsyncClient

    async def get_weather(self, city: str) -> WeatherResponse:
        params = {
            "q": city,
            "appid": self.settings.openweather_api_key,
            "units": "metric",
        }
        url = f"{self.settings.openweather_base_url}/weather"

        try:
            response = await self.client.get(
                url,
                params=params,
                timeout=self.settings.request_timeout_seconds,
            )
        except httpx.RequestError as exc:
            raise UpstreamWeatherError("Failed to reach weather provider") from exc

        if response.status_code == 404:
            raise CityNotFoundError(f"City not found: {city}")
        if response.status_code != 200:
            raise UpstreamWeatherError(
                f"Weather provider returned status {response.status_code}"
            )

        payload = response.json()
        weather_items = payload.get("weather") or []
        description = weather_items[0]["description"] if weather_items else "unknown"

        return WeatherResponse(
            city=city,
            temperature_celsius=float(payload["main"]["temp"]),
            description=description,
            humidity=int(payload["main"]["humidity"]),
            wind_speed_mps=float(payload["wind"]["speed"]),
        )

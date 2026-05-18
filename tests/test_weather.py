from unittest.mock import AsyncMock

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.dependencies import get_weather_service
from app.main import app
from app.services.weather import WeatherService

GEOCODING_FIXTURE = {
    "results": [
        {
            "name": "Osaka",
            "latitude": 34.6937,
            "longitude": 135.5023,
        }
    ]
}

FORECAST_FIXTURE = {
    "current": {
        "temperature_2m": 22.5,
        "relative_humidity_2m": 65,
        "wind_speed_10m": 3.2,
        "weather_code": 0,
    }
}


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
async def api_client(settings: Settings):
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    service = WeatherService(settings=settings, client=mock_client)
    app.dependency_overrides[get_weather_service] = lambda: service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client, mock_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_weather_success(api_client):
    client, mock_http = api_client
    mock_http.get.side_effect = [
        httpx.Response(200, json=GEOCODING_FIXTURE),
        httpx.Response(200, json=FORECAST_FIXTURE),
    ]

    response = await client.get("/weather", params={"city": "osaka"})

    assert response.status_code == 200
    assert response.json() == {
        "city": "osaka",
        "temperature_celsius": 22.5,
        "description": "clear sky",
        "humidity": 65,
        "wind_speed_mps": 3.2,
    }
    assert mock_http.get.await_count == 2

    geocoding_call = mock_http.get.await_args_list[0]
    assert geocoding_call.kwargs["params"]["name"] == "osaka"

    forecast_call = mock_http.get.await_args_list[1]
    assert forecast_call.kwargs["params"]["latitude"] == 34.6937
    assert forecast_call.kwargs["params"]["longitude"] == 135.5023
    assert forecast_call.kwargs["params"]["wind_speed_unit"] == "ms"


@pytest.mark.asyncio
async def test_get_weather_city_not_found(api_client):
    client, mock_http = api_client
    mock_http.get.return_value = httpx.Response(200, json={"results": []})

    response = await client.get("/weather", params={"city": "unknown-city"})

    assert response.status_code == 404
    assert "City not found" in response.json()["detail"]
    mock_http.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_weather_upstream_error(api_client):
    client, mock_http = api_client
    mock_http.get.return_value = httpx.Response(500, json={})

    response = await client.get("/weather", params={"city": "osaka"})

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_get_weather_missing_city(api_client):
    client, _ = api_client

    response = await client.get("/weather")

    assert response.status_code == 422

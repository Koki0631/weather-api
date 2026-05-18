from unittest.mock import AsyncMock

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.dependencies import get_weather_service
from app.main import app
from app.services.weather import WeatherService

OPENWEATHER_FIXTURE = {
    "main": {"temp": 22.5, "humidity": 65},
    "wind": {"speed": 3.2},
    "weather": [{"description": "clear sky"}],
}


@pytest.fixture
def settings() -> Settings:
    return Settings(openweather_api_key="test-key")


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
    mock_response = httpx.Response(200, json=OPENWEATHER_FIXTURE)
    mock_http.get.return_value = mock_response

    response = await client.get("/weather", params={"city": "osaka"})

    assert response.status_code == 200
    assert response.json() == {
        "city": "osaka",
        "temperature_celsius": 22.5,
        "description": "clear sky",
        "humidity": 65,
        "wind_speed_mps": 3.2,
    }
    mock_http.get.assert_awaited_once()
    call_kwargs = mock_http.get.await_args.kwargs
    assert call_kwargs["params"]["q"] == "osaka"
    assert call_kwargs["params"]["units"] == "metric"


@pytest.mark.asyncio
async def test_get_weather_city_not_found(api_client):
    client, mock_http = api_client
    mock_http.get.return_value = httpx.Response(404, json={"cod": "404"})

    response = await client.get("/weather", params={"city": "unknown-city"})

    assert response.status_code == 404
    assert "City not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_weather_upstream_error(api_client):
    client, mock_http = api_client
    mock_http.get.return_value = httpx.Response(500, json={"cod": "500"})

    response = await client.get("/weather", params={"city": "osaka"})

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_get_weather_missing_city(api_client):
    client, _ = api_client

    response = await client.get("/weather")

    assert response.status_code == 422

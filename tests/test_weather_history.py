from unittest.mock import AsyncMock

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Settings
from app.db import Base
from app.dependencies import get_weather_service
from app.main import app
from app.repositories.weather_repository import WeatherRepository
from app.services.weather import WeatherService

SAMPLE_RECORD = {
    "city": "osaka",
    "temperature_celsius": 22.5,
    "description": "clear sky",
    "humidity": 65,
    "wind_speed_mps": 3.2,
}


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
async def history_client(db_session: Session, settings: Settings):
    repository = WeatherRepository(db_session)
    service = WeatherService(
        settings=settings,
        client=AsyncMock(spec=httpx.AsyncClient),
        repository=repository,
    )
    app.dependency_overrides[get_weather_service] = lambda: service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client, repository

    app.dependency_overrides.clear()


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
async def api_client(settings: Settings):
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    service = WeatherService(settings=settings, client=mock_client, repository=None)
    app.dependency_overrides[get_weather_service] = lambda: service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_weather_history_success(history_client):
    client, repository = history_client
    repository.save_weather(**SAMPLE_RECORD)
    repository.save_weather(
        city="osaka",
        temperature_celsius=25.0,
        description="mainly clear",
        humidity=70,
        wind_speed_mps=4.0,
    )

    response = await client.get(
        "/weather/history", params={"city": "osaka", "limit": 10}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["city"] == "osaka"
    assert len(payload["items"]) == 2
    assert payload["items"][0]["temperature_celsius"] == 25.0
    assert payload["items"][1]["temperature_celsius"] == 22.5
    assert "created_at" in payload["items"][0]


@pytest.mark.asyncio
async def test_get_weather_history_empty_list(history_client):
    client, _ = history_client

    response = await client.get("/weather/history", params={"city": "osaka"})

    assert response.status_code == 200
    assert response.json() == {"city": "osaka", "items": []}


@pytest.mark.asyncio
async def test_get_weather_history_respects_limit(history_client):
    client, repository = history_client
    for temperature in (20.0, 21.0, 22.0):
        repository.save_weather(
            city="osaka",
            temperature_celsius=temperature,
            description="clear sky",
            humidity=65,
            wind_speed_mps=3.2,
        )

    response = await client.get(
        "/weather/history", params={"city": "osaka", "limit": 2}
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2


@pytest.mark.asyncio
async def test_get_weather_history_invalid_limit(api_client):
    client = api_client

    response = await client.get(
        "/weather/history", params={"city": "osaka", "limit": 0}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_weather_history_database_unavailable(api_client):
    client = api_client

    response = await client.get("/weather/history", params={"city": "osaka"})

    assert response.status_code == 503
    assert "Database is not available" in response.json()["detail"]

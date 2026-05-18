from collections.abc import AsyncIterator

import httpx
from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.services.weather import WeatherService


async def get_http_client(request: Request) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


def get_weather_service(
    settings: Settings = Depends(get_settings),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> WeatherService:
    return WeatherService(settings=settings, client=client)

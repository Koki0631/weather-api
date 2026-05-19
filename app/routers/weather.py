from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_weather_service
from app.schemas import WeatherHistoryResponse, WeatherResponse
from app.services.weather import (
    CityNotFoundError,
    DatabaseUnavailableError,
    UpstreamWeatherError,
    WeatherService,
)

router = APIRouter(tags=["weather"])


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(..., min_length=1, description="City name (e.g. osaka)"),
    service: WeatherService = Depends(get_weather_service),
) -> WeatherResponse:
    try:
        return await service.get_weather(city=city)
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UpstreamWeatherError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/weather/history", response_model=WeatherHistoryResponse)
async def get_weather_history(
    city: str = Query(..., min_length=1, description="City name (e.g. osaka)"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    service: WeatherService = Depends(get_weather_service),
) -> WeatherHistoryResponse:
    try:
        return service.get_weather_history(city=city, limit=limit)
    except DatabaseUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

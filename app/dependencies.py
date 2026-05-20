from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.user_repository import UserRepository
from app.repositories.weather_repository import WeatherRepository
from app.services.auth import AuthService
from app.services.favorites import FavoritesService
from app.services.weather import WeatherService


async def get_http_client(request: Request) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


def get_weather_repository(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session | None, Depends(get_db)],
) -> WeatherRepository | None:
    if not settings.database_enabled or db is None:
        return None
    return WeatherRepository(db)


def get_user_repository(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session | None, Depends(get_db)],
) -> UserRepository | None:
    if not settings.database_enabled or db is None:
        return None
    return UserRepository(db)


def get_auth_service(
    user_repository: Annotated[UserRepository | None, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(user_repository=user_repository)


def get_favorite_repository(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session | None, Depends(get_db)],
) -> FavoriteRepository | None:
    if not settings.database_enabled or db is None:
        return None
    return FavoriteRepository(db)


def get_favorites_service(
    repository: Annotated[FavoriteRepository | None, Depends(get_favorite_repository)],
) -> FavoritesService:
    return FavoritesService(repository=repository)


def get_weather_service(
    settings: Annotated[Settings, Depends(get_settings)],
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    repository: Annotated[WeatherRepository | None, Depends(get_weather_repository)],
) -> WeatherService:
    return WeatherService(settings=settings, client=client, repository=repository)

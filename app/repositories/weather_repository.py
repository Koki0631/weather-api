from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.weather import WeatherRecord
from app.schemas import WeatherResponse


class WeatherRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_weather(self, weather: WeatherResponse) -> None:
        today = datetime.now(UTC).date()
        existing = self._session.scalar(
            select(WeatherRecord).where(
                WeatherRecord.city == weather.city,
                func.date(WeatherRecord.created_at) == today,
            )
        )

        if existing is not None:
            existing.temperature_celsius = weather.temperature_celsius
            existing.description = weather.description
            existing.humidity = weather.humidity
            existing.wind_speed_mps = weather.wind_speed_mps
        else:
            self._session.add(
                WeatherRecord(
                    city=weather.city,
                    temperature_celsius=weather.temperature_celsius,
                    description=weather.description,
                    humidity=weather.humidity,
                    wind_speed_mps=weather.wind_speed_mps,
                    created_at=datetime.now(UTC),
                )
            )

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

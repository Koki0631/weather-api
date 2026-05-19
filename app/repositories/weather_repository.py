from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.weather import WeatherRecord
from app.schemas import WeatherResponse


class WeatherRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_weather(self, weather: WeatherResponse) -> None:
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

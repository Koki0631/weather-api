from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.weather import WeatherRecord


class WeatherRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_weather(
        self,
        *,
        city: str,
        temperature_celsius: float,
        description: str,
        humidity: int,
        wind_speed_mps: float,
    ) -> WeatherRecord:
        record = WeatherRecord(
            city=city,
            temperature_celsius=temperature_celsius,
            description=description,
            humidity=humidity,
            wind_speed_mps=wind_speed_mps,
            created_at=datetime.now(UTC),
        )
        self._session.add(record)

        try:
            self._session.commit()
            self._session.refresh(record)
            return record
        except Exception:
            self._session.rollback()
            raise

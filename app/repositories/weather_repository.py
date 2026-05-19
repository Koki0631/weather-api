from datetime import UTC, datetime

from sqlalchemy import select
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
        user_id: int | None = None,
    ) -> WeatherRecord:
        record = WeatherRecord(
            user_id=user_id,
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

    def list_by_city_and_user(
        self, *, city: str, user_id: int, limit: int
    ) -> list[WeatherRecord]:
        statement = (
            select(WeatherRecord)
            .where(
                WeatherRecord.city == city,
                WeatherRecord.user_id == user_id,
            )
            .order_by(WeatherRecord.created_at.desc())
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

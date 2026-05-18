from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.weather import WeatherRecord


class WeatherRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_weather(
        self, *, city: str, temperature: float, description: str
    ) -> None:
        today = datetime.now(UTC).date()
        existing = self._session.scalar(
            select(WeatherRecord).where(
                WeatherRecord.city == city,
                func.date(WeatherRecord.created_at) == today,
            )
        )

        if existing is not None:
            existing.temperature = temperature
            existing.description = description
        else:
            self._session.add(
                WeatherRecord(
                    city=city,
                    temperature=temperature,
                    description=description,
                    created_at=datetime.now(UTC),
                )
            )

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

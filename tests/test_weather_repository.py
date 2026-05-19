import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models.weather import WeatherRecord
from app.repositories.weather_repository import WeatherRepository
from app.schemas import WeatherResponse

SAMPLE_WEATHER = WeatherResponse(
    city="osaka",
    temperature_celsius=22.5,
    description="clear sky",
    humidity=65,
    wind_speed_mps=3.2,
)


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_save_weather_inserts_new_record(db_session: Session) -> None:
    repo = WeatherRepository(db_session)
    repo.save_weather(SAMPLE_WEATHER)

    record = db_session.scalar(
        select(WeatherRecord).where(WeatherRecord.city == "osaka")
    )
    assert record is not None
    assert record.temperature_celsius == 22.5
    assert record.description == "clear sky"
    assert record.humidity == 65
    assert record.wind_speed_mps == 3.2


def test_save_weather_inserts_multiple_records_for_same_city(
    db_session: Session,
) -> None:
    repo = WeatherRepository(db_session)
    repo.save_weather(SAMPLE_WEATHER)
    updated = SAMPLE_WEATHER.model_copy(
        update={
            "temperature_celsius": 25.0,
            "description": "mainly clear",
            "humidity": 70,
            "wind_speed_mps": 4.0,
        }
    )
    repo.save_weather(updated)

    rows = db_session.scalars(
        select(WeatherRecord).where(WeatherRecord.city == "osaka")
    ).all()
    assert len(rows) == 2
    assert rows[0].temperature_celsius == 22.5
    assert rows[1].temperature_celsius == 25.0
    assert rows[1].description == "mainly clear"

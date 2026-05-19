import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models.weather import WeatherRecord
from app.repositories.weather_repository import WeatherRepository

SAMPLE_WEATHER = {
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


def test_save_weather_inserts_new_record(db_session: Session) -> None:
    repo = WeatherRepository(db_session)
    record = repo.save_weather(**SAMPLE_WEATHER, user_id=1)

    assert record.id is not None
    assert record.user_id == 1
    assert record.city == "osaka"


def test_list_by_city_and_user_filters_records(db_session: Session) -> None:
    repo = WeatherRepository(db_session)
    repo.save_weather(**SAMPLE_WEATHER, user_id=1)
    repo.save_weather(**SAMPLE_WEATHER, user_id=2)
    repo.save_weather(
        city="tokyo",
        temperature_celsius=18.0,
        description="cloudy",
        humidity=80,
        wind_speed_mps=2.0,
        user_id=1,
    )

    records = repo.list_by_city_and_user(city="osaka", user_id=1, limit=10)

    assert len(records) == 1
    assert records[0].user_id == 1
    assert records[0].city == "osaka"

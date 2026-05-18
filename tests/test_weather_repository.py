import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models.weather import WeatherRecord
from app.repositories.weather_repository import WeatherRepository


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_upsert_inserts_new_record(db_session: Session) -> None:
    repo = WeatherRepository(db_session)
    repo.upsert_weather(city="osaka", temperature=20.0, description="clear sky")

    record = db_session.scalar(
        select(WeatherRecord).where(WeatherRecord.city == "osaka")
    )
    assert record is not None
    assert record.temperature == 20.0
    assert record.description == "clear sky"


def test_upsert_updates_existing_record_for_same_city_and_day(
    db_session: Session,
) -> None:
    repo = WeatherRepository(db_session)
    repo.upsert_weather(city="osaka", temperature=20.0, description="clear sky")
    repo.upsert_weather(city="osaka", temperature=25.0, description="mainly clear")

    rows = db_session.scalars(
        select(WeatherRecord).where(WeatherRecord.city == "osaka")
    ).all()
    assert len(rows) == 1
    assert rows[0].temperature == 25.0
    assert rows[0].description == "mainly clear"

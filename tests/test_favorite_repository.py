import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.repositories.favorite_repository import FavoriteRepository

SAMPLE_CITY = "osaka"


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_add_and_list_by_user(db_session: Session) -> None:
    repo = FavoriteRepository(db_session)
    record = repo.add(user_id=1, city=SAMPLE_CITY, memo="note")

    assert record.id is not None
    assert record.user_id == 1
    assert record.city == SAMPLE_CITY
    assert record.memo == "note"

    records = repo.list_by_user(user_id=1)
    assert len(records) == 1
    assert records[0].city == SAMPLE_CITY


def test_get_by_user_and_city_returns_existing(db_session: Session) -> None:
    repo = FavoriteRepository(db_session)
    repo.add(user_id=1, city=SAMPLE_CITY)

    found = repo.get_by_user_and_city(user_id=1, city=SAMPLE_CITY)

    assert found is not None
    assert found.city == SAMPLE_CITY


def test_delete_by_user_and_city(db_session: Session) -> None:
    repo = FavoriteRepository(db_session)
    repo.add(user_id=1, city=SAMPLE_CITY)

    deleted = repo.delete_by_user_and_city(user_id=1, city=SAMPLE_CITY)

    assert deleted is True
    assert repo.list_by_user(user_id=1) == []


def test_delete_returns_false_when_missing(db_session: Session) -> None:
    repo = FavoriteRepository(db_session)

    assert repo.delete_by_user_and_city(user_id=1, city=SAMPLE_CITY) is False


def test_list_by_user_is_scoped(db_session: Session) -> None:
    repo = FavoriteRepository(db_session)
    repo.add(user_id=1, city="osaka")
    repo.add(user_id=2, city="tokyo")

    assert len(repo.list_by_user(user_id=1)) == 1
    assert repo.list_by_user(user_id=1)[0].city == "osaka"

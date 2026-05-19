from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.db import Base, get_engine, get_session_local
from app.models.user import User
from app.seed import seed_test_user


def _reset_db_globals() -> None:
    import app.db as db_module

    db_module._engine = None
    db_module._SessionLocal = None


def test_seed_test_user_is_idempotent() -> None:
    _reset_db_globals()
    settings = Settings(
        database_url="sqlite:///:memory:",
        database_enabled=True,
        seed_test_user=True,
        test_user_email="seed@example.com",
        test_user_password="secret",
    )
    engine = get_engine(settings)
    Base.metadata.create_all(bind=engine)

    seed_test_user(settings)
    seed_test_user(settings)

    with get_session_local()() as session:
        count = session.scalar(select(func.count()).select_from(User))
    assert count == 1


def test_seed_test_user_skipped_when_disabled() -> None:
    _reset_db_globals()
    settings = Settings(
        database_url="sqlite:///:memory:",
        database_enabled=True,
        seed_test_user=False,
    )
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)

    seed_test_user(settings)

    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(User))
    assert count == 0

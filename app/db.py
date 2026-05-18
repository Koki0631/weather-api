import logging
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine(settings: Settings | None = None):
    global _engine, _SessionLocal
    settings = settings or get_settings()
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_session_local() -> sessionmaker[Session]:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def get_db() -> Generator[Session | None, None, None]:
    settings = get_settings()
    if not settings.database_enabled:
        yield None
        return

    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models.weather import WeatherRecord  # noqa: F401

    settings = get_settings()
    if not settings.database_enabled:
        return

    try:
        Base.metadata.create_all(bind=get_engine(settings))
    except Exception:
        logger.exception("Failed to initialize database tables")

import logging

from app.auth.password import hash_password
from app.config import Settings, get_settings
from app.db import get_engine, get_session_local
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


def seed_test_user(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not settings.database_enabled or not settings.seed_test_user:
        return

    try:
        get_engine(settings)
        session_local = get_session_local()
    except Exception:
        logger.exception("Failed to connect for test user seed")
        return

    with session_local() as session:
        repo = UserRepository(session)
        if repo.get_by_email(settings.test_user_email) is not None:
            logger.info("Test user already exists: %s", settings.test_user_email)
            return

        session.add(
            User(
                email=settings.test_user_email,
                hashed_password=hash_password(settings.test_user_password),
            )
        )
        session.commit()
        logger.info("Created test user: %s", settings.test_user_email)

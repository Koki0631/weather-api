import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.config import Settings
from app.db import Base
from app.dependencies import get_auth_service
from app.main import app
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth import AuthService

TEST_EMAIL = "user@example.com"
TEST_PASSWORD = "secret-password"


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            email=TEST_EMAIL,
            hashed_password=hash_password(TEST_PASSWORD),
        )
        session.add(user)
        session.commit()
        yield session


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
async def auth_client(db_session: Session, settings: Settings):
    repository = UserRepository(db_session)
    service = AuthService(user_repository=repository)
    app.dependency_overrides[get_auth_service] = lambda: service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_client_no_db(settings: Settings):
    service = AuthService(user_repository=None)
    app.dependency_overrides[get_auth_service] = lambda: service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_success_returns_bearer_token(auth_client):
    response = await auth_client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


@pytest.mark.asyncio
async def test_login_invalid_password_returns_401(auth_client):
    response = await auth_client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(auth_client):
    response = await auth_client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": TEST_PASSWORD},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_database_unavailable_returns_503(auth_client_no_db):
    response = await auth_client_no_db.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )

    assert response.status_code == 503

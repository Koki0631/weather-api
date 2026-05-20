import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.jwt import create_access_token
from app.db import Base
from app.dependencies import get_favorites_service
from app.main import app
from app.models.user import User
from app.repositories.favorite_repository import FavoriteRepository
from app.services.favorites import FavoritesService

CURRENT_USER_ID = 1
OTHER_USER_ID = 2


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                User(
                    id=CURRENT_USER_ID, email="one@example.com", hashed_password="hash"
                ),
                User(id=OTHER_USER_ID, email="two@example.com", hashed_password="hash"),
            ]
        )
        session.commit()
        yield session


@pytest.fixture
async def favorites_client(db_session: Session):
    repository = FavoriteRepository(db_session)
    service = FavoritesService(repository=repository)
    app.dependency_overrides[get_favorites_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: CURRENT_USER_ID

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client, repository

    app.dependency_overrides.clear()


@pytest.fixture
async def api_client():
    service = FavoritesService(repository=None)
    app.dependency_overrides[get_favorites_service] = lambda: service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


def _auth_headers(user_id: int = CURRENT_USER_ID) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


@pytest.mark.asyncio
async def test_add_favorite_success(favorites_client) -> None:
    client, _ = favorites_client

    response = await client.post(
        "/favorites",
        json={"city": "osaka"},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["city"] == "osaka"
    assert payload["id"] is not None
    assert "created_at" in payload


@pytest.mark.asyncio
async def test_add_favorite_is_idempotent(favorites_client) -> None:
    client, _ = favorites_client

    first = await client.post(
        "/favorites",
        json={"city": "osaka"},
        headers=_auth_headers(),
    )
    second = await client.post(
        "/favorites",
        json={"city": "osaka"},
        headers=_auth_headers(),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.asyncio
async def test_list_favorites_returns_only_current_user(favorites_client) -> None:
    client, repository = favorites_client
    repository.add(user_id=CURRENT_USER_ID, city="osaka")
    repository.add(user_id=CURRENT_USER_ID, city="tokyo")
    repository.add(user_id=OTHER_USER_ID, city="osaka")

    response = await client.get("/favorites", headers=_auth_headers())

    assert response.status_code == 200
    cities = {item["city"] for item in response.json()["items"]}
    assert cities == {"osaka", "tokyo"}


@pytest.mark.asyncio
async def test_delete_favorite_success(favorites_client) -> None:
    client, repository = favorites_client
    repository.add(user_id=CURRENT_USER_ID, city="osaka")

    response = await client.delete("/favorites/osaka", headers=_auth_headers())

    assert response.status_code == 204
    assert repository.list_by_user(user_id=CURRENT_USER_ID) == []


@pytest.mark.asyncio
async def test_delete_favorite_not_found(favorites_client) -> None:
    client, _ = favorites_client

    response = await client.delete("/favorites/osaka", headers=_auth_headers())

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_does_not_remove_other_users_favorite(favorites_client) -> None:
    client, repository = favorites_client
    repository.add(user_id=OTHER_USER_ID, city="osaka")

    response = await client.delete("/favorites/osaka", headers=_auth_headers())

    assert response.status_code == 404
    assert len(repository.list_by_user(user_id=OTHER_USER_ID)) == 1


@pytest.mark.asyncio
async def test_favorites_require_authentication(favorites_client) -> None:
    client, _ = favorites_client
    app.dependency_overrides.pop(get_current_user, None)

    response = await client.get("/favorites")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_favorites_database_unavailable(api_client) -> None:
    app.dependency_overrides[get_current_user] = lambda: CURRENT_USER_ID
    client = api_client

    response = await client.get("/favorites", headers=_auth_headers())

    assert response.status_code == 503
    app.dependency_overrides.clear()

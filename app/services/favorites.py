from dataclasses import dataclass

from app.models.favorite import Favorite
from app.repositories.favorite_repository import FavoriteRepository
from app.schemas import FavoriteItem, FavoriteListResponse


class DatabaseUnavailableError(Exception):
    pass


class FavoriteNotFoundError(Exception):
    pass


def _to_item(record: Favorite) -> FavoriteItem:
    return FavoriteItem(
        id=record.id,
        city=record.city,
        memo=record.memo,
        created_at=record.created_at,
    )


@dataclass(frozen=True)
class FavoritesService:
    repository: FavoriteRepository | None

    def add_favorite(
        self, *, user_id: int, city: str, memo: str | None = None
    ) -> FavoriteItem:
        if self.repository is None:
            raise DatabaseUnavailableError("Database is not available")

        existing = self.repository.get_by_user_and_city(user_id=user_id, city=city)
        if existing is not None:
            return _to_item(existing)

        record = self.repository.add(user_id=user_id, city=city, memo=memo)
        return _to_item(record)

    def list_favorites(self, *, user_id: int) -> FavoriteListResponse:
        if self.repository is None:
            raise DatabaseUnavailableError("Database is not available")

        records = self.repository.list_by_user(user_id=user_id)
        return FavoriteListResponse(items=[_to_item(record) for record in records])

    def remove_favorite(self, *, user_id: int, city: str) -> None:
        if self.repository is None:
            raise DatabaseUnavailableError("Database is not available")

        deleted = self.repository.delete_by_user_and_city(user_id=user_id, city=city)
        if not deleted:
            raise FavoriteNotFoundError(f"Favorite city not found: {city}")

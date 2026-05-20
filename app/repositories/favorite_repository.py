from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user_and_city(self, *, user_id: int, city: str) -> Favorite | None:
        statement = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.city == city,
        )
        return self._session.scalar(statement)

    def add(self, *, user_id: int, city: str, memo: str | None = None) -> Favorite:
        record = Favorite(user_id=user_id, city=city, memo=memo)
        self._session.add(record)

        try:
            self._session.commit()
            self._session.refresh(record)
            return record
        except Exception:
            self._session.rollback()
            raise

    def list_by_user(self, *, user_id: int) -> list[Favorite]:
        statement = (
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        return list(self._session.scalars(statement).all())

    def delete_by_user_and_city(self, *, user_id: int, city: str) -> bool:
        record = self.get_by_user_and_city(user_id=user_id, city=city)
        if record is None:
            return False

        self._session.delete(record)
        try:
            self._session.commit()
            return True
        except Exception:
            self._session.rollback()
            raise

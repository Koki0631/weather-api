from dataclasses import dataclass

from app.auth.jwt import create_access_token
from app.auth.password import verify_password
from app.repositories.user_repository import UserRepository


class InvalidCredentialsError(Exception):
    pass


class DatabaseUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class AuthService:
    user_repository: UserRepository | None

    def login(self, email: str, password: str) -> str:
        if self.user_repository is None:
            raise DatabaseUnavailableError("Database is not available")

        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        return create_access_token(user.id)

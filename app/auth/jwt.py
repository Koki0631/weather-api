from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
_FALLBACK_SECRET_KEY = "dev-only-set-secret-key-in-env"


def _get_secret_key() -> str:
    secret_key = get_settings().secret_key
    if secret_key:
        return secret_key
    return _FALLBACK_SECRET_KEY


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, _get_secret_key(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])


__all__ = ["ALGORITHM", "JWTError", "create_access_token", "decode_access_token"]

from datetime import UTC, datetime, timedelta

from jose import jwt

from app.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1
_FALLBACK_SECRET_KEY = "dev-only-set-secret-key-in-env"


def _get_secret_key() -> str:
    secret_key = get_settings().secret_key
    if secret_key:
        return secret_key
    return _FALLBACK_SECRET_KEY


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, _get_secret_key(), algorithm=ALGORITHM)

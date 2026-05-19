from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth.deps import get_current_user
from app.auth.jwt import ALGORITHM, create_access_token
from app.config import get_settings


def test_get_current_user_returns_user_id_from_valid_token() -> None:
    user_id = get_current_user(token=create_access_token(42))

    assert user_id == 42


def test_get_current_user_rejects_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="not-a-valid-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


def test_get_current_user_rejects_expired_token() -> None:
    settings = get_settings()
    expired_token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(hours=1)},
        settings.secret_key,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=expired_token)

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_token_without_sub() -> None:
    settings = get_settings()
    token = jwt.encode(
        {"exp": datetime.now(UTC) + timedelta(days=1)},
        settings.secret_key,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token)

    assert exc_info.value.status_code == 401

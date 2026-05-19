from datetime import UTC, datetime, timedelta

from jose import jwt

from app.auth.jwt import ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS, create_access_token
from app.config import get_settings


def test_create_access_token_includes_sub_and_exp() -> None:
    token = create_access_token(42)
    settings = get_settings()

    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

    assert payload["sub"] == "42"
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    expected_min = datetime.now(UTC) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS - 0.01)
    expected_max = datetime.now(UTC) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS + 0.01)
    assert expected_min <= exp <= expected_max

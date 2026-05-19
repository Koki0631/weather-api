from app.auth.password import hash_password, verify_password


def test_hash_password_returns_bcrypt_hash() -> None:
    hashed = hash_password("secret-password")

    assert hashed.startswith("$2b$")
    assert hashed != "secret-password"


def test_verify_password_accepts_correct_plain_text() -> None:
    hashed = hash_password("secret-password")

    assert verify_password("secret-password", hashed) is True


def test_verify_password_rejects_wrong_plain_text() -> None:
    hashed = hash_password("secret-password")

    assert verify_password("wrong-password", hashed) is False

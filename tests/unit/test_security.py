from datetime import UTC, datetime, timedelta

import pytest

from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


def test_password_hash_is_not_plaintext() -> None:
    password = "correct-horse-battery"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("incorrect-password", hashed)


def test_password_hashes_are_salted() -> None:
    password = "correct-horse-battery"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_access_token_round_trip() -> None:
    token = create_access_token("42")

    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert "exp" in payload


def test_expired_access_token_is_rejected() -> None:
    expired = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "42", "exp": expired},
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(token)


@pytest.mark.parametrize(
    "token",
    ["", "not-a-jwt", "a.b.c", "eyJhbGciOiJub25lIn0.eyJzdWIiOiI0MiJ9."],
)
def test_malformed_or_untrusted_tokens_are_rejected(token: str) -> None:
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(token)


def test_token_signed_with_unconfigured_algorithm_is_rejected() -> None:
    token = jwt.encode(
        {"sub": "42", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.secret_key,
        algorithm="HS384",
    )

    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(token)

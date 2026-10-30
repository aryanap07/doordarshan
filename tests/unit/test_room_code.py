import re

import pytest


from app.core.room_code import ALPHABET, generate_room_code

pytestmark = pytest.mark.unit


def test_default_room_code_has_expected_length_and_alphabet() -> None:
    room_code = generate_room_code()

    assert len(room_code) == 8
    assert re.fullmatch(r"[A-Z0-9]{8}", room_code)
    assert set(room_code) <= set(ALPHABET)


@pytest.mark.parametrize("length", [1, 4, 12, 32])
def test_room_code_respects_requested_length(length: int) -> None:
    assert len(generate_room_code(length)) == length


def test_zero_length_room_code_is_empty() -> None:
    assert generate_room_code(0) == ""

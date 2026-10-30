import json

import pytest

from app.ws.constants import MAX_MESSAGE_SIZE
from app.ws.exceptions import MessageValidationError
from app.ws.messages import (
    AnswerMessage,
    DirectMessage,
    ICECandidateMessage,
    LeaveMessage,
    OfferMessage,
    PingMessage,
    PongAckMessage,
)
from app.ws.validators import parse_message

pytestmark = pytest.mark.websocket


@pytest.mark.parametrize(
    ("payload", "expected_type"),
    [
        ({"type": "ping"}, PingMessage),
        ({"type": "pong"}, PongAckMessage),
        ({"type": "leave"}, LeaveMessage),
        ({"type": "offer", "target_user_id": 2, "sdp": "offer-sdp"}, OfferMessage),
        ({"type": "answer", "target_user_id": 2, "sdp": "answer-sdp"}, AnswerMessage),
        (
            {
                "type": "ice_candidate",
                "target_user_id": 2,
                "candidate": {"candidate": "candidate:1"},
            },
            ICECandidateMessage,
        ),
        (
            {"type": "direct_message", "target_user_id": 2, "content": "hello"},
            DirectMessage,
        ),
    ],
)
def test_parse_message_supports_known_message_types(payload, expected_type) -> None:
    parsed = parse_message(json.dumps(payload))

    assert isinstance(parsed, expected_type)


def test_parse_message_ignores_unknown_extra_fields() -> None:
    parsed = parse_message(json.dumps({"type": "ping", "client_metadata": "ignored"}))

    assert isinstance(parsed, PingMessage)


@pytest.mark.parametrize("raw", ["{", "not-json", "[1, 2]", "null", '"text"'])
def test_parse_message_rejects_malformed_or_non_object_json(raw: str) -> None:
    with pytest.raises(MessageValidationError):
        parse_message(raw)


def test_parse_message_rejects_missing_type() -> None:
    with pytest.raises(MessageValidationError, match="Missing required field"):
        parse_message("{}")


def test_parse_message_rejects_unknown_type() -> None:
    with pytest.raises(MessageValidationError, match="Unsupported message type"):
        parse_message('{"type":"run_shell"}')


def test_parse_message_rejects_invalid_required_fields() -> None:
    with pytest.raises(MessageValidationError, match="target_user_id"):
        parse_message('{"type":"offer","sdp":"offer-sdp"}')


def test_parse_message_rejects_oversized_payload() -> None:
    raw = json.dumps(
        {
            "type": "direct_message",
            "target_user_id": 2,
            "content": "x" * MAX_MESSAGE_SIZE,
        }
    )

    with pytest.raises(MessageValidationError, match="size limit"):
        parse_message(raw)


def test_direct_message_content_has_maximum_length() -> None:
    raw = json.dumps(
        {
            "type": "direct_message",
            "target_user_id": 2,
            "content": "x" * 4097,
        }
    )

    with pytest.raises(MessageValidationError, match="content"):
        parse_message(raw)

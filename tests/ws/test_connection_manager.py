from __future__ import annotations

from typing import Any

import pytest

from app.ws.connection_manager import ConnectionManager
from app.ws.messages import DirectMessage, ParticipantJoinedMessage

pytestmark = pytest.mark.websocket


class FakeWebSocket:
    def __init__(self, *, fail_send: bool = False) -> None:
        self.accepted = False
        self.sent: list[dict[str, Any]] = []
        self.fail_send = fail_send

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, payload: dict[str, Any]) -> None:
        if self.fail_send:
            raise RuntimeError("simulated send failure")
        self.sent.append(payload)


@pytest.mark.asyncio
async def test_connect_sends_participant_list_and_broadcasts_join() -> None:
    manager = ConnectionManager()
    first = FakeWebSocket()
    second = FakeWebSocket()

    await manager.connect(first, "ROOM1234", 1, "first")
    await manager.connect(second, "ROOM1234", 2, "second")

    assert first.accepted is True
    assert second.accepted is True
    assert first.sent[0]["type"] == "participant_list"
    assert first.sent[-1] == {
        "type": "participant_joined",
        "user_id": 2,
        "username": "second",
    }
    assert second.sent[-1]["participants"] == [{"user_id": 1, "username": "first"}]
    assert manager.total_connections == 2
    assert manager.total_rooms == 1


@pytest.mark.asyncio
async def test_send_to_returns_false_when_target_is_missing() -> None:
    manager = ConnectionManager()

    sent = await manager.send_to(
        "ROOM1234",
        999,
        DirectMessage(target_user_id=999, content="hello"),
    )

    assert sent is False


@pytest.mark.asyncio
async def test_send_to_delivers_message_to_target() -> None:
    manager = ConnectionManager()
    websocket = FakeWebSocket()
    await manager.connect(websocket, "ROOM1234", 1, "first")

    sent = await manager.send_to(
        "ROOM1234",
        1,
        DirectMessage(target_user_id=1, content="hello"),
    )

    assert sent is True
    assert websocket.sent[-1] == {
        "type": "direct_message",
        "target_user_id": 1,
        "content": "hello",
    }


@pytest.mark.asyncio
async def test_disconnect_notifies_remaining_participants_and_cleans_room() -> None:
    manager = ConnectionManager()
    first = FakeWebSocket()
    second = FakeWebSocket()
    await manager.connect(first, "ROOM1234", 1, "first")
    await manager.connect(second, "ROOM1234", 2, "second")

    await manager.disconnect(second)
    await manager.disconnect(first)

    left_messages = [
        message for message in first.sent if message["type"] == "participant_left"
    ]
    assert left_messages == [
        {"type": "participant_left", "user_id": 2, "username": "second"}
    ]
    assert manager.total_connections == 0
    assert manager.total_rooms == 0


@pytest.mark.asyncio
async def test_reconnecting_same_user_replaces_previous_socket() -> None:
    manager = ConnectionManager()
    old_socket = FakeWebSocket()
    new_socket = FakeWebSocket()

    await manager.connect(old_socket, "ROOM1234", 7, "same-user")
    await manager.connect(new_socket, "ROOM1234", 7, "same-user")

    assert manager.get_participant_by_ws(old_socket) is None
    assert manager.get_participant_by_ws(new_socket) is not None
    assert manager.total_connections == 1
    assert manager.list_participants("ROOM1234")[0].websocket is new_socket


@pytest.mark.asyncio
async def test_disconnect_is_idempotent_for_unknown_socket() -> None:
    manager = ConnectionManager()

    await manager.disconnect(FakeWebSocket())

    assert manager.total_connections == 0
    assert manager.total_rooms == 0


@pytest.mark.asyncio
async def test_send_to_reports_failed_websocket_send() -> None:
    manager = ConnectionManager()
    websocket = FakeWebSocket(fail_send=True)
    await manager.connect(websocket, "ROOM1234", 1, "first")

    # The initial list send fails, but the connection remains registered.
    sent = await manager.send_to(
        "ROOM1234",
        1,
        DirectMessage(target_user_id=1, content="hello"),
    )

    assert sent is False


@pytest.mark.asyncio
async def test_broadcast_can_exclude_a_participant() -> None:
    manager = ConnectionManager()
    first = FakeWebSocket()
    second = FakeWebSocket()
    await manager.connect(first, "ROOM1234", 1, "first")
    await manager.connect(second, "ROOM1234", 2, "second")
    first.sent.clear()
    second.sent.clear()

    await manager.broadcast(
        "ROOM1234",
        ParticipantJoinedMessage(user_id=3, username="third"),
        exclude_user_id=1,
    )

    assert first.sent == []
    assert second.sent[-1]["user_id"] == 3

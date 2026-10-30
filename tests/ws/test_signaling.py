from __future__ import annotations

from typing import Any

import pytest

from app.ws.connection_manager import ConnectedParticipant, manager
from app.ws.exceptions import GracefulDisconnect, TargetNotFoundError
from app.ws.handlers import dispatch_message
from app.ws.messages import DirectMessage, LeaveMessage, PingMessage

pytestmark = pytest.mark.websocket


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    async def send_json(self, payload: dict[str, Any]) -> None:
        self.sent.append(payload)


@pytest.mark.asyncio
async def test_dispatch_ping_sends_pong() -> None:
    websocket = FakeWebSocket()
    participant = ConnectedParticipant(1, "alice", websocket, "ROOM1234")

    await dispatch_message(websocket, participant, PingMessage())

    assert websocket.sent == [{"type": "pong"}]


@pytest.mark.asyncio
async def test_dispatch_leave_requests_graceful_disconnect() -> None:
    websocket = FakeWebSocket()
    participant = ConnectedParticipant(1, "alice", websocket, "ROOM1234")

    with pytest.raises(GracefulDisconnect):
        await dispatch_message(websocket, participant, LeaveMessage())


@pytest.mark.asyncio
async def test_dispatch_direct_message_rejects_missing_recipient() -> None:
    manager._rooms.clear()
    manager._reverse.clear()
    websocket = FakeWebSocket()
    participant = ConnectedParticipant(1, "alice", websocket, "ROOM1234")

    with pytest.raises(TargetNotFoundError):
        await dispatch_message(
            websocket,
            participant,
            DirectMessage(target_user_id=99, content="hello"),
        )

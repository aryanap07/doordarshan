import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


from app.models import User

pytestmark = pytest.mark.websocket


def test_websocket_requires_token(client: TestClient) -> None:
    try:
        with client.websocket_connect("/ws/rooms/ROOM1234"):
            raise AssertionError("WebSocket should reject a missing token")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_websocket_rejects_invalid_token(client: TestClient) -> None:
    try:
        with client.websocket_connect("/ws/rooms/ROOM1234?token=not-a-valid-token"):
            raise AssertionError("WebSocket should reject an invalid token")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_websocket_rejects_unknown_room(
    client: TestClient,
    make_user,
    make_token,
) -> None:
    user: User = make_user()
    token = make_token(user)

    try:
        with client.websocket_connect(f"/ws/rooms/UNKNOWN1?token={token}"):
            raise AssertionError("WebSocket should reject an unknown room")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_websocket_rejects_inactive_room(
    client: TestClient,
    make_user,
    make_room,
    make_token,
) -> None:
    user: User = make_user()
    room = make_room(host=user, is_active=False)
    token = make_token(user)

    try:
        with client.websocket_connect(f"/ws/rooms/{room.room_code}?token={token}"):
            raise AssertionError("WebSocket should reject an inactive room")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_websocket_connects_and_handles_ping(
    client: TestClient,
    make_user,
    make_room,
    make_token,
) -> None:
    user: User = make_user()
    room = make_room(host=user)
    token = make_token(user)

    with client.websocket_connect(
        f"/ws/rooms/{room.room_code}?token={token}"
    ) as websocket:
        participant_list = websocket.receive_json()
        assert participant_list["type"] == "participant_list"
        assert participant_list["participants"] == []

        websocket.send_json({"type": "ping"})
        pong = websocket.receive_json()
        assert pong == {"type": "pong"}


def test_websocket_relays_direct_messages_between_room_members(
    client: TestClient,
    make_user,
    make_room,
    make_token,
) -> None:
    first_user = make_user(username="first", email="first@example.com")
    second_user = make_user(username="second", email="second@example.com")
    room = make_room(host=first_user)
    first_token = make_token(first_user)
    second_token = make_token(second_user)

    with client.websocket_connect(
        f"/ws/rooms/{room.room_code}?token={first_token}"
    ) as first_socket:
        assert first_socket.receive_json()["type"] == "participant_list"

        with client.websocket_connect(
            f"/ws/rooms/{room.room_code}?token={second_token}"
        ) as second_socket:
            assert second_socket.receive_json()["participants"] == [
                {"user_id": first_user.id, "username": "first"}
            ]
            joined = first_socket.receive_json()
            assert joined == {
                "type": "participant_joined",
                "user_id": second_user.id,
                "username": "second",
            }

            second_socket.send_json(
                {
                    "type": "direct_message",
                    "target_user_id": first_user.id,
                    "content": "hello from second",
                }
            )
            relayed = first_socket.receive_json()
            assert relayed == {
                "type": "direct_message",
                "from_user_id": second_user.id,
                "content": "hello from second",
            }

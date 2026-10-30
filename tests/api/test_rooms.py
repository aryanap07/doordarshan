import pytest
from fastapi.testclient import TestClient


from app.models import User

pytestmark = pytest.mark.api


ROOMS = "/api/v1/rooms"


def test_create_room_requires_authentication(client: TestClient) -> None:
    response = client.post(ROOMS, json={"title": "Planning"})

    assert response.status_code == 401


def test_create_room_generates_room_code(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    host: User = make_user()

    response = client.post(
        ROOMS,
        json={"title": "Planning"},
        headers=auth_headers(host),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Planning"
    assert body["host_id"] == host.id
    assert len(body["room_code"]) == 8
    assert body["is_active"] is True


def test_room_title_validation(client: TestClient, make_user, auth_headers) -> None:
    host = make_user()

    empty = client.post(ROOMS, json={"title": ""}, headers=auth_headers(host))
    too_long = client.post(
        ROOMS,
        json={"title": "x" * 101},
        headers=auth_headers(host),
    )

    assert empty.status_code == 422
    assert too_long.status_code == 422


def test_list_and_get_rooms(client: TestClient, make_user, make_room) -> None:
    host = make_user()
    room = make_room(host=host)

    listing = client.get(ROOMS)
    detail = client.get(f"{ROOMS}/{room.room_code}")

    assert listing.status_code == 200
    assert [item["room_code"] for item in listing.json()] == [room.room_code]
    assert detail.status_code == 200
    assert detail.json()["id"] == room.id


def test_get_unknown_room_returns_404(client: TestClient) -> None:
    response = client.get(f"{ROOMS}/UNKNOWN1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"


def test_only_room_host_can_delete_room(
    client: TestClient,
    make_user,
    make_room,
    auth_headers,
) -> None:
    host = make_user(username="host", email="host@example.com")
    guest = make_user(username="guest", email="guest@example.com")
    room = make_room(host=host)

    forbidden = client.delete(
        f"{ROOMS}/{room.room_code}",
        headers=auth_headers(guest),
    )
    deleted = client.delete(
        f"{ROOMS}/{room.room_code}",
        headers=auth_headers(host),
    )

    assert forbidden.status_code == 403
    assert deleted.status_code == 204
    assert client.get(f"{ROOMS}/{room.room_code}").status_code == 404


def test_delete_unknown_room_returns_404(
    client: TestClient, make_user, auth_headers
) -> None:
    user = make_user()

    response = client.delete(f"{ROOMS}/UNKNOWN1", headers=auth_headers(user))

    assert response.status_code == 404


def test_join_room_is_idempotent_and_leave_marks_participant(
    client: TestClient,
    make_user,
    make_room,
    auth_headers,
) -> None:
    host = make_user(username="host", email="host@example.com")
    room = make_room(host=host)
    headers = auth_headers(host)

    first_join = client.post(f"{ROOMS}/{room.room_code}/join", headers=headers)
    second_join = client.post(f"{ROOMS}/{room.room_code}/join", headers=headers)

    assert first_join.status_code == 200
    assert second_join.status_code == 200
    assert first_join.json()["id"] == second_join.json()["id"]

    left = client.post(f"{ROOMS}/{room.room_code}/leave", headers=headers)

    assert left.status_code == 200
    assert left.json()["left_at"] is not None
    assert client.get(f"{ROOMS}/{room.room_code}/participants").json() == []


def test_join_unknown_room_returns_404(
    client: TestClient, make_user, auth_headers
) -> None:
    user = make_user()

    response = client.post(f"{ROOMS}/UNKNOWN1/join", headers=auth_headers(user))

    assert response.status_code == 404


def test_leave_without_active_participation_returns_404(
    client: TestClient,
    make_user,
    make_room,
    auth_headers,
) -> None:
    host = make_user()
    room = make_room(host=host)

    response = client.post(
        f"{ROOMS}/{room.room_code}/leave",
        headers=auth_headers(host),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found."


def test_list_participants_only_returns_active_participants(
    client: TestClient,
    make_user,
    make_room,
    auth_headers,
) -> None:
    host = make_user(username="host", email="host@example.com")
    guest = make_user(username="guest", email="guest@example.com")
    room = make_room(host=host)
    client.post(f"{ROOMS}/{room.room_code}/join", headers=auth_headers(host))
    client.post(f"{ROOMS}/{room.room_code}/join", headers=auth_headers(guest))

    response = client.get(f"{ROOMS}/{room.room_code}/participants")

    assert response.status_code == 200
    assert {item["user_id"] for item in response.json()} == {host.id, guest.id}

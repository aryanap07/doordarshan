import pytest
from fastapi.testclient import TestClient


from app.models import User

pytestmark = pytest.mark.api


MEETINGS = "/api/v1/meetings"


def test_create_meeting_requires_authentication(client: TestClient) -> None:
    response = client.post(MEETINGS, json={"title": "Planning"})

    assert response.status_code == 401


def test_create_and_read_meeting(
    client: TestClient,
    make_user,
    make_room,
    auth_headers,
) -> None:
    host: User = make_user()
    room = make_room(host=host)

    created = client.post(
        MEETINGS,
        json={
            "title": "Planning",
            "description": "Quarterly planning",
            "room_id": room.id,
        },
        headers=auth_headers(host),
    )

    assert created.status_code == 201
    meeting_id = created.json()["id"]
    assert created.json()["host_id"] == host.id
    assert created.json()["room_id"] == room.id

    detail = client.get(f"{MEETINGS}/{meeting_id}")
    listing = client.get(MEETINGS)

    assert detail.status_code == 200
    assert detail.json()["title"] == "Planning"
    assert any(item["id"] == meeting_id for item in listing.json())


def test_meeting_title_and_room_id_validation(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    host = make_user()
    headers = auth_headers(host)

    blank_title = client.post(MEETINGS, json={"title": ""}, headers=headers)
    invalid_room = client.post(
        MEETINGS,
        json={"title": "Planning", "room_id": 0},
        headers=headers,
    )

    assert blank_title.status_code == 422
    assert invalid_room.status_code == 422


def test_meeting_host_can_update_meeting(
    client: TestClient,
    make_user,
    make_meeting,
    auth_headers,
) -> None:
    host = make_user()
    meeting = make_meeting(host=host)

    response = client.put(
        f"{MEETINGS}/{meeting.id}",
        json={"title": "Updated Planning", "description": "New agenda"},
        headers=auth_headers(host),
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Planning"
    assert response.json()["description"] == "New agenda"


def test_non_host_cannot_update_meeting(
    client: TestClient,
    make_user,
    make_meeting,
    auth_headers,
) -> None:
    host = make_user(username="host", email="host@example.com")
    other = make_user(username="other", email="other@example.com")
    meeting = make_meeting(host=host)

    response = client.put(
        f"{MEETINGS}/{meeting.id}",
        json={"title": "Unauthorized edit"},
        headers=auth_headers(other),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only the meeting host can perform this action."


def test_get_missing_meeting_returns_404(client: TestClient) -> None:
    response = client.get(f"{MEETINGS}/99999")

    assert response.status_code == 404


def test_meeting_id_must_be_positive(client: TestClient) -> None:
    response = client.get(f"{MEETINGS}/0")

    assert response.status_code == 422


def test_meeting_host_can_delete_meeting(
    client: TestClient,
    make_user,
    make_meeting,
    auth_headers,
) -> None:
    host = make_user()
    meeting = make_meeting(host=host)

    response = client.delete(f"{MEETINGS}/{meeting.id}", headers=auth_headers(host))

    assert response.status_code == 204
    assert client.get(f"{MEETINGS}/{meeting.id}").status_code == 404


def test_non_host_cannot_delete_meeting(
    client: TestClient,
    make_user,
    make_meeting,
    auth_headers,
) -> None:
    host = make_user(username="host", email="host@example.com")
    other = make_user(username="other", email="other@example.com")
    meeting = make_meeting(host=host)

    response = client.delete(f"{MEETINGS}/{meeting.id}", headers=auth_headers(other))

    assert response.status_code == 403
    assert client.get(f"{MEETINGS}/{meeting.id}").status_code == 200

import pytest
from fastapi.testclient import TestClient


from app.models import User

pytestmark = pytest.mark.api


RECORDINGS = "/api/v1/recordings"


def test_create_recording_requires_authentication(client: TestClient) -> None:
    response = client.post(
        RECORDINGS,
        json={"meeting_id": 1, "file_url": "https://cdn.example.test/a.mp4"},
    )

    assert response.status_code == 401


def test_create_recording_requires_existing_meeting(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    user = make_user()

    response = client.post(
        RECORDINGS,
        json={"meeting_id": 999, "file_url": "https://cdn.example.test/a.mp4"},
        headers=auth_headers(user),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting not found."


def test_create_and_fetch_recording(
    client: TestClient,
    make_user,
    make_meeting,
    auth_headers,
) -> None:
    creator: User = make_user()
    meeting = make_meeting(host=creator)

    created = client.post(
        RECORDINGS,
        json={
            "meeting_id": meeting.id,
            "file_url": "https://cdn.example.test/meeting.mp4",
            "duration_seconds": 180,
        },
        headers=auth_headers(creator),
    )

    assert created.status_code == 201
    recording_id = created.json()["id"]
    assert created.json()["creator_id"] == creator.id
    assert created.json()["duration_seconds"] == 180

    fetched = client.get(f"{RECORDINGS}/{recording_id}")
    listing = client.get(RECORDINGS)

    assert fetched.status_code == 200
    assert fetched.json()["file_url"] == "https://cdn.example.test/meeting.mp4"
    assert any(item["id"] == recording_id for item in listing.json())


def test_recording_validation_rejects_invalid_values(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    user = make_user()

    negative_duration = client.post(
        RECORDINGS,
        json={
            "meeting_id": 1,
            "file_url": "https://cdn.example.test/a.mp4",
            "duration_seconds": -1,
        },
        headers=auth_headers(user),
    )
    invalid_meeting_id = client.post(
        RECORDINGS,
        json={"meeting_id": 0, "file_url": "https://cdn.example.test/a.mp4"},
        headers=auth_headers(user),
    )

    assert negative_duration.status_code == 422
    assert invalid_meeting_id.status_code == 422


def test_only_recording_creator_can_delete_recording(
    client: TestClient,
    make_user,
    make_meeting,
    make_recording,
    auth_headers,
) -> None:
    creator = make_user(username="creator", email="creator@example.com")
    other = make_user(username="other", email="other@example.com")
    meeting = make_meeting(host=creator)
    recording = make_recording(meeting=meeting, creator=creator)

    forbidden = client.delete(
        f"{RECORDINGS}/{recording.id}",
        headers=auth_headers(other),
    )
    deleted = client.delete(
        f"{RECORDINGS}/{recording.id}",
        headers=auth_headers(creator),
    )

    assert forbidden.status_code == 403
    assert deleted.status_code == 204
    assert client.get(f"{RECORDINGS}/{recording.id}").status_code == 404


def test_get_missing_recording_returns_404(client: TestClient) -> None:
    assert client.get(f"{RECORDINGS}/99999").status_code == 404


def test_recording_id_must_be_positive(client: TestClient) -> None:
    assert client.get(f"{RECORDINGS}/0").status_code == 422

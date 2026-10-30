import pytest
from fastapi.testclient import TestClient

from app.models import User

pytestmark = pytest.mark.api


def test_current_user_returns_authenticated_profile(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    user: User = make_user(username="profile_user", email="profile@example.com")

    response = client.get("/api/v1/users/me", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "username": "profile_user",
        "email": "profile@example.com",
    }
    assert "password_hash" not in response.json()


def test_ice_configuration_returns_stun_and_turn_servers(client: TestClient) -> None:
    response = client.get("/api/v1/ice/config")

    assert response.status_code == 200
    body = response.json()
    assert "iceServers" in body
    assert any(server["urls"][0].startswith("stun:") for server in body["iceServers"])
    turn_server = next(
        server for server in body["iceServers"] if server["urls"][0].startswith("turn:")
    )
    assert turn_server["username"] == "test-metered-user"
    assert turn_server["credential"] == "test-metered-credential"

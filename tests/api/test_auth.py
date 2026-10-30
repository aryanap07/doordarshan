import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


def test_register_creates_user_without_exposing_password_hash(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "ankur_dev",
            "email": "ankur@example.com",
            "password": "correct-horse-battery",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "ankur_dev"
    assert body["email"] == "ankur@example.com"
    assert isinstance(body["id"], int)
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "username": "first_user",
        "email": "duplicate@example.com",
        "password": "correct-horse-battery",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    duplicate = {**payload, "username": "second_user"}
    response = client.post("/api/v1/auth/register", json=duplicate)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_rejects_duplicate_username(client: TestClient) -> None:
    payload = {
        "username": "same_username",
        "email": "first@example.com",
        "password": "correct-horse-battery",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    duplicate = {**payload, "email": "second@example.com"}
    response = client.post("/api/v1/auth/register", json=duplicate)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_register_validates_username_password_and_email(client: TestClient) -> None:
    cases = [
        {"username": "ab", "email": "valid@example.com", "password": "long-password"},
        {"username": "valid", "email": "not-an-email", "password": "long-password"},
        {"username": "valid", "email": "valid@example.com", "password": "short"},
    ]

    for payload in cases:
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422


def test_login_returns_bearer_token(client: TestClient) -> None:
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_user",
            "email": "login@example.com",
            "password": "correct-horse-battery",
        },
    )
    assert registration.status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "correct-horse-battery"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_rejects_wrong_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_user",
            "email": "login@example.com",
            "password": "correct-horse-battery",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "incorrect-password"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "missing@example.com", "password": "irrelevant-password"},
    )

    assert response.status_code == 401


def test_current_user_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

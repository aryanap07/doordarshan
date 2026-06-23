# Tests for the doordarshan FastAPI application
# Uses TestClient for both HTTP and WebSocket testing.
from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200


def test_websocket_connect():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/testroom") as websocket:
            assert websocket is not None

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


@pytest.mark.parametrize(
    ("path", "expected_fragment"),
    [
        ("/", "<!DOCTYPE html>"),
        ("/login", "<!DOCTYPE html>"),
        ("/register", "<!DOCTYPE html>"),
        ("/dashboard", "<!DOCTYPE html>"),
        ("/room", "<!DOCTYPE html>"),
    ],
)
def test_frontend_pages_are_served(
    client: TestClient,
    path: str,
    expected_fragment: str,
) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert expected_fragment.lower() in response.text.lower()


def test_static_assets_are_served(client: TestClient) -> None:
    css = client.get("/css/style.css")
    javascript = client.get("/js/api.js")

    assert css.status_code == 200
    assert javascript.status_code == 200

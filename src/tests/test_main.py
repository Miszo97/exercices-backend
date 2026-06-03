from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_set_auth_token_view():
    payload = {"username": "testuser", "password": "secret"}
    response = client.post("/set-auth-token", json=payload)

    assert response.status_code == 200

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_set_auth_token_view():
    response = client.post("/api/v1/auth/token", data={"password": "secret"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "access_token" in response.cookies

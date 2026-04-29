from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)  # Create a TestClient instance using the FastAPI app


def test_set_auth_token_view():
    # Example payload for setting an auth token
    payload = {"username": "testuser", "password": "secret"}

    # Assuming there's an endpoint "/set-auth-token" for setting the auth token
    response = client.post("/set-auth-token", json=payload)

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200
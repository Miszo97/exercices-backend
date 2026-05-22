from datetime import datetime

from fastapi.testclient import TestClient

from database_models import DurationExerciseEntry, RepsExerciseEntry
from exercises_sources.sql import SQLExerciseSource
from src.main import app

client = TestClient(app)
source = SQLExerciseSource()

from unittest.mock import MagicMock
import pytest
from src.main import app, get_service, check_access_key


@pytest.fixture
def mock_service():
    service = MagicMock()
    return service


@pytest.fixture(autouse=True)
def setup_dependency_overrides(mock_service: MagicMock):
    app.dependency_overrides[get_service] = lambda: mock_service
    app.dependency_overrides[check_access_key] = lambda: True

    yield

    app.dependency_overrides.clear()


def test_read_today_json__integration(session):
    session.add_all(
        [
            DurationExerciseEntry(date=datetime.now(), name="plank", duration=60),
            DurationExerciseEntry(date=datetime.now(), name="plank", duration=20),
            RepsExerciseEntry(date=datetime.now(), name="push ups", reps=20),
            RepsExerciseEntry(date=datetime.now(), name="push ups", reps=25),
        ]
    )
    session.commit()
    app.dependency_overrides[SQLExerciseSource] = lambda: source

    response = client.get("/today")
    assert response.status_code == 200
    assert response.json() == {
        "exercises": {
            "push ups": 45,
            "plank": 80,
        }
    }


class TestGetToday:
    def test_get(self, mock_service: MagicMock):
        mock_service.sum_exercises_for_day.return_value = {
            "push ups": 45,
            "plank": 80
        }

        response = client.get("/today")

        assert response.status_code == 200
        assert response.json() == {
            "exercises": {
                "push ups": 45,
                "plank": 80
            }
        }

        mock_service.sum_exercises_for_day.assert_called_once()

    def test_get_no_data(self, mock_service: MagicMock):
        mock_service.sum_exercises_for_day.return_value = {}

        response = client.get("/today")

        assert response.status_code == 200
        assert response.json() == {
            "exercises": {}
        }

        mock_service.sum_exercises_for_day.assert_called_once()


class TestCreateDurationEntry:
    def test_post(self, mock_service: MagicMock):
        now = datetime.now()
        mock_service.add_duration_exercise.return_value = {
            "id": 1,
            "date": now,
            "name": "plank",
            "duration": 60
        }

        response = client.post("/duration", json={"name": "plank", "duration": 60})

        assert response.status_code == 200
        assert response.json() == {
            'data': {
                'date': now.isoformat(),
                'duration': 60,
                'id': 1,
                'name': 'plank',
                'type': 'duration',
            },
            'status': 'ok',
        }
        mock_service.add_duration_exercise.assert_called_once()

    def test_post_400(self, mock_service: MagicMock):
        response = client.post("/duration", json={"nam": "plank", "dura": 60})
        assert response.status_code == 422
        assert len(response.json()["detail"]) == 2
        assert response.json()["detail"][0]["type"] == "missing"
        assert response.json()["detail"][1]["type"] == "missing"


class Test401NotAuthenticated:
    def test_unauthenticated_table(self):
        response = client.get("/table")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_today(self):
        response = client.get("/today")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_exercises(self):
        response = client.get("/exercises")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_exercise_stats(self):
        response = client.get("/exercises/plank/stats")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_post_duration(self):
        response = client.post("/duration", json={"name": "plank", "duration": 60})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_post_reps(self):
        response = client.post("/reps", json={"name": "push ups", "reps": 10})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

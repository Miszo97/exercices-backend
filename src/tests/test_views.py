from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from src.dtos import ExerciseHistoryEntry, RepsExerciseStats, DurationExerciseStats
from src.exercises_sources.sql import SQLExerciseSource
from src.main import app
from src.dtos import (
    DurationExerciseEntry,
    RepsExerciseDaySum)

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


class TestGetToday:
    def test_get(self, mock_service: MagicMock):
        mock_service.sum_exercises_for_day.return_value = {
            "push ups": 45,
            "plank": 80
        }

        response = client.get("/api/v1/summary")

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

        response = client.get("/api/v1/summary")

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

        response = client.post(
            "/api/v1/exercises",
            json={"type": "duration", "name": "plank", "duration": 60},
        )

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
        response = client.post("/api/v1/exercises", json={"type": "duration"})
        assert response.status_code == 422
        assert len(response.json()["detail"]) == 2
        assert response.json()["detail"][0]["type"] == "missing"
        assert response.json()["detail"][1]["type"] == "missing"


class TestCreateRepsEntry:
    def test_post(self, mock_service: MagicMock):
        now = datetime.now()
        mock_service.add_reps_exercise.return_value = {
            "id": 1,
            "date": now,
            "name": "push ups",
            "reps": 10
        }

        response = client.post(
            "/api/v1/exercises",
            json={"type": "reps", "name": "push ups", "reps": 10},
        )

        assert response.status_code == 200
        assert response.json() == {
            'data': {
                'date': now.isoformat(),
                'reps': 10,
                'id': 1,
                'name': 'push ups',
                'type': 'reps',
            },
            'status': 'ok',
        }
        mock_service.add_reps_exercise.assert_called_once()

    def test_post_400(self, mock_service: MagicMock):
        response = client.post("/api/v1/exercises", json={"type": "reps"})
        assert response.status_code == 422
        assert len(response.json()["detail"]) == 2
        assert response.json()["detail"][0]["type"] == "missing"
        assert response.json()["detail"][1]["type"] == "missing"


def test_get_exercise_history(mock_service: MagicMock):
    now_str = datetime.now().isoformat()
    mock_service.get_exercise_history.return_value = [
        ExerciseHistoryEntry(name="push ups", reps=10, date=now_str),
        ExerciseHistoryEntry(name="push ups", reps=15, date=now_str),
    ]
    response = client.get("/api/v1/exercises/push ups")
    assert response.status_code == 200
    assert response.json() == [
        {
            "date": now_str,
            "name": "push ups",
            "reps": 10,
            "duration": None
        },
        {
            "date": now_str,
            "name": "push ups",
            "reps": 15,
            "duration": None
        }
    ]


def test_read_root_table_view_with_mock(mock_service: MagicMock):
    mock_service.fetch_exercises.return_value = []

    response = client.get("/table")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # Check that fetch_exercises was called with limit=10000 as defined in the view
    mock_service.fetch_exercises.assert_called_once_with(limit=10000)


class TestGetExerciseStats:
    def test_reps_stats(self, mock_service: MagicMock):
        mock_service.get_exercise_stats.return_value = RepsExerciseStats(
            total_reps=150,
            reps_in_last_30_days=50
        )
        response = client.get("/api/v1/exercises/push ups/stats")
        assert response.status_code == 200
        assert response.json() == {
            "total_reps": 150,
            "reps_in_last_30_days": 50
        }
        mock_service.get_exercise_stats.assert_called_once_with(name="push ups")

    def test_duration_stats(self, mock_service: MagicMock):
        mock_service.get_exercise_stats.return_value = DurationExerciseStats(
            total_duration=3600,
            duration_in_last_30_days=600
        )
        response = client.get("/api/v1/exercises/plank/stats")
        assert response.status_code == 200
        assert response.json() == {
            "total_duration": 3600,
            "duration_in_last_30_days": 600
        }
        mock_service.get_exercise_stats.assert_called_once_with(name="plank")

    def test_stats_none(self, mock_service: MagicMock):
        mock_service.get_exercise_stats.return_value = None
        response = client.get("/api/v1/exercises/unknown/stats")
        assert response.status_code == 404
        assert response.json()["detail"] == "Exercise stats not found"


class TestGetExercises:
    def test_get_exercises(self, mock_service: MagicMock):
        mock_service.fetch_exercises.return_value = [
            DurationExerciseEntry(name="plank", duration=60, date=datetime.now()),
            RepsExerciseDaySum(name="push ups", reps=10, date=datetime.now()),
        ]
        response = client.get("/api/v1/exercises")
        assert response.status_code == 200
        assert response.json() == {
            "exercises": [
                {
                    'date': datetime.now().date().isoformat(),
                    'duration': 60,
                    'name': 'plank',
                    'reps': None,
                },
            ],
        }


class Test401NotAuthenticated:
    @pytest.fixture(autouse=True)
    def require_real_auth(self, setup_dependency_overrides, monkeypatch):
        # Undo the module-level check_access_key override so the real dependency runs,
        # and give it a hash that no empty/absent credential can match.
        monkeypatch.setenv("ACCESS_KEY_HASH", "unmatchable")
        app.dependency_overrides.pop(check_access_key, None)
        yield

    def test_unauthenticated_table(self):
        response = client.get("/table")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_summary(self):
        response = client.get("/api/v1/summary")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_exercises(self):
        response = client.get("/api/v1/exercises")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_exercise_stats(self):
        response = client.get("/api/v1/exercises/plank/stats")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_post_duration(self):
        response = client.post(
            "/api/v1/exercises",
            json={"type": "duration", "name": "plank", "duration": 60},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

    def test_unauthenticated_post_reps(self):
        response = client.post(
            "/api/v1/exercises",
            json={"type": "reps", "name": "push ups", "reps": 10},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid access key"

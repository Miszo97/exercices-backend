from datetime import datetime

from fastapi.testclient import TestClient

from database_models import DurationExerciseEntry, RepsExerciseEntry
from exercises_sources.sql import SQLExerciseSource
from src.main import app

client = TestClient(app)
source = SQLExerciseSource()


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

    response = client.get("/today")
    assert response.status_code == 200
    assert response.json() == {
        "exercises": {
            "push ups": 45,
            "plank": 80,
        }
    }


class Test401NotAuthenticated:
    def test_unauthenticated_table(self):
        response = client.get("/table")
        assert response.status_code == 401

    def test_unauthenticated_today(self):
        response = client.get("/today")
        assert response.status_code == 401

    def test_unauthenticated_exercises(self):
        response = client.get("/exercises")
        assert response.status_code == 401

    def test_unauthenticated_exercise_stats(self):
        response = client.get("/exercises/plank/stats")
        assert response.status_code == 401

    def test_unauthenticated_post_duration(self):
        response = client.post("/duration", json={"name": "plank", "duration": 60})
        assert response.status_code == 401

    def test_unauthenticated_post_reps(self):
        response = client.post("/reps", json={"name": "push ups", "reps": 10})
        assert response.status_code == 401

from datetime import datetime

from fastapi.testclient import TestClient

from database_models import DurationExerciseEntry, RepsExerciseEntry
from exercises_sources.sql import SQLExerciseSource
from src.main import app

client = TestClient(app)
source = SQLExerciseSource()


def test_read_today_json(session):
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

from datetime import datetime

from fastapi.testclient import TestClient

from database_models import DurationExerciseEntry, RepsExerciseEntry
from exercises_sources.sql import SQLExerciseSource
from src.main import app, check_access_key

import pytest

client = TestClient(app)
source = SQLExerciseSource()


@pytest.fixture(autouse=True)
def setup_access_key_override():
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

    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    assert response.json() == {
        "exercises": {
            "push ups": 45,
            "plank": 80,
        }
    }

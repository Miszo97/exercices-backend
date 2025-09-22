import sys
import types
from datetime import datetime

import pytest

from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def patch_firebase_modules(monkeypatch):
    # Create a lightweight fake firebase_admin module so importing src.main won't
    # try to initialize real Firebase credentials in the test environment.
    fake_firestore = types.SimpleNamespace(client=lambda: "fake-db")
    fake_firebase_admin = types.SimpleNamespace(
        initialize_app=lambda *a, **k: None,
        firestore=fake_firestore,
    )
    monkeypatch.setitem(sys.modules, "firebase_admin", fake_firebase_admin)
    # Also ensure submodule path works for `from firebase_admin import firestore`.
    monkeypatch.setitem(sys.modules, "firebase_admin.firestore", fake_firestore)
    yield


def test_read_today_json_returns_transformed_summary(monkeypatch):
    # Import here after firebase is patched
    from src import main
    from src.dtos import (
        RepsExerciseDaySum,
        DurationExerciseDaySum,
        ExerciseType,
    )

    # Prepare controlled return from sum_exercises regardless of fetch output
    today = datetime.now().date()
    summed = [
        RepsExerciseDaySum(name="Push-up", reps=25, date=today),
        DurationExerciseDaySum(name="Running", duration=0, unit="minutes", date=today),
        DurationExerciseDaySum(name="Cycling", duration=45, unit="minutes", date=today),
    ]

    # Patch fetch_exercises and sum_exercises used inside src.main
    monkeypatch.setattr(main, "fetch_exercises", lambda db, day=None: ["ignored"])
    monkeypatch.setattr(main, "sum_exercises", lambda _result: summed)

    client = TestClient(main.app)
    resp = client.get("/today")

    assert resp.status_code == 200
    # Validate JSON transformation logic
    assert resp.json() == [
        {"name": "Push-up", "type": ExerciseType.REPS.value, "reps": 25, "duration": None},
        {"name": "Running", "type": ExerciseType.DURATION.value, "reps": None, "duration": None},
        {"name": "Cycling", "type": ExerciseType.DURATION.value, "reps": None, "duration": 45},
    ]

from datetime import datetime

from src.dtos import ExerciseDay, ExerciseEntry
from src.fetching_exercises import sum_exercises


def test_sum_exercises():
    today = datetime.now()
    exercises = [
        ExerciseEntry(name="Push-up", reps=10, duration=None, unit=None, date=today),
        ExerciseEntry(name="Push-up", reps=15, duration=None, unit=None, date=today),
        ExerciseEntry(name="Running", reps=None, duration=30, unit="minutes", date=today),
        ExerciseEntry(name="Running", reps=None, duration=20, unit="minutes", date=today),
        ExerciseEntry(name="Cycling", reps=None, duration=45, unit="minutes", date=today),
    ]
    summed = sum_exercises(exercises)
    assert len(summed) == 3
    assert summed == [
        ExerciseDay(
            name="Push-up", reps=25, duration=0, unit=None, date=today.date()
        ),
        ExerciseDay(
            name="Running", reps=0, duration=50, unit="minutes", date=today.date()
        ),
        ExerciseDay(
            name="Cycling", reps=0, duration=45, unit="minutes", date=today.date()
        )
    ]


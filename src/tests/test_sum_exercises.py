from datetime import datetime

from src.dtos import (
    RepsExerciseEntry,
    DurationExerciseEntry,
    RepsExerciseDaySum,
    DurationExerciseDaySum,
)
from src.fetching_exercises import sum_exercises


def test_sum_exercises():
    today = datetime.now()
    exercises = [
        RepsExerciseEntry(name="Push-up", reps=10, date=today),
        RepsExerciseEntry(name="Push-up", reps=15, date=today),
        DurationExerciseEntry(
            name="Running", duration=30, unit="minutes", date=today
        ),
        DurationExerciseEntry(
            name="Running", duration=20, unit="minutes", date=today
        ),
        DurationExerciseEntry(
            name="Cycling", duration=45, unit="minutes", date=today
        ),
    ]
    summed = sum_exercises(exercises)
    assert len(summed) == 3
    assert summed == [
        RepsExerciseDaySum(name="Push-up", reps=25, date=today.date()),
        DurationExerciseDaySum(
            name="Running", duration=50, unit="minutes", date=today.date()
        ),
        DurationExerciseDaySum(
            name="Cycling", duration=45, unit="minutes", date=today.date()
        ),
    ]

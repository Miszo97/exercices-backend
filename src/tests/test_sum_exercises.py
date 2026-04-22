from datetime import datetime

from src.dtos import (
    DurationExerciseDaySum,
    RepsExerciseDaySum,
    RepsExerciseEntry,
    dfs,
)
from src.fetching_exercises import sum_exercises


def test_sum_exercises():
    today = datetime.now()
    exercises = [
        RepsExerciseEntry(name="Push-up", reps=10, date=today),
        RepsExerciseEntry(name="Push-up", reps=15, date=today),
        dfs(name="Running", duration=30, date=today),
        dfs(name="Running", duration=20, date=today),
        dfs(name="Cycling", duration=45, date=today),
    ]
    summed = sum_exercises(exercises)
    assert len(summed) == 3
    assert summed == [
        RepsExerciseDaySum(name="Push-up", reps=25, date=today.date()),
        DurationExerciseDaySum(name="Running", duration=50, date=today.date()),
        DurationExerciseDaySum(name="Cycling", duration=45, date=today.date()),
    ]

from datetime import date
from typing import Dict, List

from src.dtos import DurationExerciseStats, ExerciseEntryAbstract, RepsExerciseStats
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.exercises_sources.exercises_source import ExerciseSource
from src.exercises_sources.sql import SQLExerciseSource
from src.fetching_exercises import sum_exercises


class ExerciseService:
    def __init__(self, exercise_source: ExerciseSource = None):
        if exercise_source is None:
            self.exercise_source = SQLExerciseSource()
        else:
            self.exercise_source = exercise_source

    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        return self.exercise_source.add_reps_exercise(request=request)

    def add_duration_exercise(self, request: AddDurationExercisesRequest):
        return self.exercise_source.add_duration_exercise(request=request)

    def fetch_exercises(
        self,
        day: date = None,
        limit: int = None,
        offset: int = 0,
        last_days: int = None,
    ) -> List[ExerciseEntryAbstract]:
        return self.exercise_source.fetch_exercises(
            day=day, limit=limit, offset=offset, last_days=last_days
        )

    def sum_exercises_for_day(
        self,
        day: date = None,
    ) -> Dict[str, int]:
        return self.exercise_source.sum_exercises_for_day(day=day)

    def get_exercise_stats(
        self, name: str
    ) -> RepsExerciseStats | DurationExerciseStats:
        return self.exercise_source.get_exercise_stats(name=name)

    def get_exercise_history(
        self,
        name: str,
        last_days: int | None = None,
    ) -> list[dict]:
        entries = self.exercise_source.fetch_exercises_by_name(
            name=name, last_days=last_days
        )
        summed = sum_exercises(entries)
        return summed.model_dump()["exercises"]

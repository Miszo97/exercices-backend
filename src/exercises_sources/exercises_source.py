import abc
from datetime import date
from typing import List

from src.dtos import DurationExerciseStats, ExerciseEntryAbstract, RepsExerciseStats
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)


class ExerciseSource(abc.ABC):
    @abc.abstractmethod
    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        pass

    @abc.abstractmethod
    def add_duration_exercise(self, request: AddDurationExercisesRequest):
        pass

    @abc.abstractmethod
    def fetch_exercises(
        self, day: date = None, limit=None, offset=None, last_days: int = None
    ) -> List[ExerciseEntryAbstract]:
        """Fetch exercises with optional time window.
        - day: restrict to a specific calendar day
        - last_days: restrict to last N days (ignored if day is provided)
        - limit/offset: pagination applied after sorting by date ascending
        """
        pass

    @abc.abstractmethod
    def fetch_exercises_by_name(
        self,
        name: str,
        day: date = None,
        limit: int | None = None,
        offset: int | None = None,
        last_days: int | None = None,
    ) -> List[ExerciseEntryAbstract]:
        """Fetch exercises filtered by exact exercise `name` with the same time window semantics as `fetch_exercises`."""
        pass

    @abc.abstractmethod
    def get_exercise_stats(
        self, name: str
    ) -> RepsExerciseStats | DurationExerciseStats:
        pass

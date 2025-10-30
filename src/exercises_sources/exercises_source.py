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
        pass

    @abc.abstractmethod
    def get_exercise_stats(
        self, name: str
    ) -> RepsExerciseStats | DurationExerciseStats:
        pass

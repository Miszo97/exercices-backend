import abc
from datetime import date
from typing import Dict, List, Protocol, Any

from src.dtos import DurationExerciseStats, ExerciseEntryAbstract, RepsExerciseStats
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)


class ExerciseSource(Protocol):
    def add_reps_exercise(self, request: AddRepsExercisesRequest) -> Dict[str, Any]: ...

    def add_duration_exercise(self, request: AddDurationExercisesRequest) -> Dict[str, Any]: ...

    def fetch_exercises(
        self, day: date = None, limit=None, offset=None, last_days: int = None
    ) -> List[ExerciseEntryAbstract]: ...

    def sum_exercises_for_day(self, day: date = None) -> Dict[str, int]: ...

    def fetch_exercises_by_name(
        self,
        name: str,
        day: date = None,
        limit: int | None = None,
        offset: int | None = None,
        last_days: int | None = None,
    ) -> List[ExerciseEntryAbstract]: ...

    def get_exercise_stats(
        self, name: str
    ) -> RepsExerciseStats | DurationExerciseStats: ...

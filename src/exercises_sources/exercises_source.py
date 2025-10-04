import abc
from datetime import date
from typing import List

from dtos import ExerciseEntryAbstract
from exercises_sources.dtos import AddDurationExercisesRequest, AddRepsExercisesRequest


class ExerciseSource(abc.ABC):
    @abc.abstractmethod
    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        pass

    @abc.abstractmethod
    def add_duration_exercise(self, request: AddDurationExercisesRequest):
        pass

    @abc.abstractmethod
    def fetch_exercises(
        self, day: date = None, limit=None, offset=None
    ) -> List[ExerciseEntryAbstract]:
        pass

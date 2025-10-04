import abc
from datetime import date
from typing import List

from dtos import ExerciseEntryAbstract


class ExerciseSource(abc.ABC):
    @abc.abstractmethod
    def add_reps_exercise(self, name, reps, unit=None):
        pass

    @abc.abstractmethod
    def add_duration_exercise(self, name, duration, unit="seconds"):
        pass

    @abc.abstractmethod
    def fetch_exercises(self, day: date = None) -> List[ExerciseEntryAbstract]:
        pass

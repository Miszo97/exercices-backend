from datetime import date, datetime
from enum import Enum

from dataclasses import dataclass


class ExerciseType(Enum):
    REPS = "reps"
    DURATION = "duration"


# The newer, more granular DTOs can remain for potential future use
@dataclass
class ExerciseEntryAbstract:
    date: datetime
    name: str


@dataclass
class ExerciseDaySumAbstract:
    date: date
    name: str


@dataclass
class RepsExerciseEntry(ExerciseEntryAbstract):
    reps: int


@dataclass
class DurationExerciseEntry(ExerciseEntryAbstract):
    duration: int
    unit: str


@dataclass
class RepsExerciseDaySum(ExerciseDaySumAbstract):
    reps: int | None = None


@dataclass
class DurationExerciseDaySum(ExerciseDaySumAbstract):
    duration: int | None = None
    unit: str | None = None


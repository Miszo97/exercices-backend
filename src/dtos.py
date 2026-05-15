from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, field_serializer


class ExerciseType(Enum):
    REPS = "reps"
    DURATION = "duration"


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


@dataclass
class RepsExerciseDaySum(ExerciseDaySumAbstract):
    reps: int | None = None


@dataclass
class DurationExerciseDaySum(ExerciseDaySumAbstract):
    duration: int | None = None


class RepsExerciseInput(BaseModel):
    name: str
    reps: int


class DurationExerciseInput(BaseModel):
    name: str
    duration: int


class ExercisesDaySumOutput(BaseModel):
    exercises: list[ExerciseDaySumAbstract]

    @field_serializer("exercises")
    def serialize_exercises(self, exercises: list[ExerciseDaySumAbstract], _info):
        return [
            {
                "date": ex.date.isoformat(),
                "name": ex.name,
                "reps": getattr(ex, "reps", None),
                "duration": getattr(ex, "duration", None),
            }
            for ex in exercises
        ]


class RepsExerciseStats(BaseModel):
    total_reps: int | None = None
    reps_in_last_30_days: int | None = None


class DurationExerciseStats(BaseModel):
    total_duration: int | None = None
    duration_in_last_30_days: int | None = None


class AddedRepsExerciseResponse(BaseModel):
    """Response after adding a reps-based exercise."""

    id: int
    date: datetime
    name: str
    reps: int
    type: str = "reps"


class AddedDurationExerciseResponse(BaseModel):
    """Response after adding a duration-based exercise."""

    id: int
    date: datetime
    name: str
    duration: int
    type: str = "duration"


class AddExerciseResponse(BaseModel):
    """Wrapper response for exercise creation endpoints."""

    status: str = "ok"
    data: AddedRepsExerciseResponse | AddedDurationExerciseResponse


class TodaySummaryResponse(BaseModel):
    """Summary of exercises performed today, mapping exercise name to total value."""

    exercises: dict[str, int]


class ExerciseHistoryEntry(BaseModel):
    """A single day-summed exercise entry in history."""

    date: str
    name: str
    reps: int | None = None
    duration: int | None = None


class StatusResponse(BaseModel):
    """Generic status response."""

    status: str = "ok"

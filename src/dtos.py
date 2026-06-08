from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, field_serializer


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


class CreateRepsExercise(BaseModel):
    type: Literal["reps"]
    name: str
    reps: int


class CreateDurationExercise(BaseModel):
    type: Literal["duration"]
    name: str
    duration: int


# Discriminated body for `POST /api/v1/exercises`. The `type` field routes to the
# matching variant, unifying the former `/reps` and `/duration` endpoints.
CreateExerciseInput = Annotated[
    Union[CreateRepsExercise, CreateDurationExercise],
    Field(discriminator="type"),
]


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
    id: int
    date: datetime
    name: str
    reps: int
    type: str = "reps"


class AddedDurationExerciseResponse(BaseModel):
    id: int
    date: datetime
    name: str
    duration: int
    type: str = "duration"


class AddExerciseResponse(BaseModel):
    status: str = "ok"
    data: AddedRepsExerciseResponse | AddedDurationExerciseResponse


class TodaySummaryResponse(BaseModel):
    exercises: dict[str, int]


class ExerciseHistoryEntry(BaseModel):
    date: str
    name: str
    reps: int | None = None
    duration: int | None = None


class StatusResponse(BaseModel):
    status: str = "ok"

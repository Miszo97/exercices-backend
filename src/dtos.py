from datetime import date, datetime
from enum import Enum

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, field_serializer, model_serializer


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
    unit: str


@dataclass
class RepsExerciseDaySum(ExerciseDaySumAbstract):
    reps: int | None = None


@dataclass
class DurationExerciseDaySum(ExerciseDaySumAbstract):
    duration: int | None = None
    unit: str | None = None


class RepsExerciseInput(BaseModel):
    name: str
    reps: int


class DurationExerciseInput(BaseModel):
    name: str
    duration: int
    unit: str


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
                "unit": getattr(ex, "unit", None),
            }
            for ex in exercises
        ]


def test_serialization():
    output = ExercisesDaySumOutput(
        exercises=[
            RepsExerciseDaySum(date=date(2024, 1, 1), name="Push-up", reps=30),
            DurationExerciseDaySum(
                date=date(2024, 1, 1), name="Running", duration=45, unit="minutes"
            ),
        ]
    )
    print(output.model_dump_json(indent=2))

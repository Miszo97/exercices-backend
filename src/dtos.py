import dataclasses
from datetime import date, datetime


@dataclasses.dataclass
class ExerciseEntry:
    date: datetime
    name: str
    reps: int | None = None
    duration: int | None = None
    unit: str | None = None

@dataclasses.dataclass
class ExerciseDay:
    date: date
    name: str
    reps: int | None = None
    duration: int | None = None
    unit: str | None = None

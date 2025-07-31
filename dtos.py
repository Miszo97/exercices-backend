import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Exercise:
    date: datetime
    name: str
    reps: int | None = None
    duration: int | None = None
    unit: str | None = None

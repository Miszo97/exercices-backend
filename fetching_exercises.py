import dataclasses
from datetime import datetime, timedelta
from typing import List


@dataclasses.dataclass
class Exercise:
    date: datetime
    name: str
    reps: int | None = None
    duration: int | None = None
    unit: str | None = None


def fetch_exercises(db, day: datetime = None) -> List[Exercise]:
    exercises_ref = db.collection('exercises').order_by('date')

    if day:
        start_of_day = datetime(day.year, day.month, day.day)
        end_of_day = start_of_day + timedelta(days=1)
        docs = exercises_ref.where('date', '>=', start_of_day).where('date', '<', end_of_day).stream()
    else:
        docs = exercises_ref.stream()

    exercises = []
    for doc in docs:
        data = doc.to_dict()
        print(f"Fetched data: {data}")  # Debugging line
        exercise = Exercise(
            date=data.get('date'),
            name=data.get('name'),
            reps=data.get('reps'),
            duration=data.get('duration'),
            unit=data.get('unit')
        )
        exercises.append(exercise)

    return exercises
from datetime import date, datetime, timedelta
from typing import List

from dtos import Exercise


def fetch_exercises(db, day: date = None) -> List[Exercise]:
    exercises_ref = db.collection("exercises").order_by("date")

    if day:
        # Filtruj tylko po dacie (ignorując czas)
        docs = (
            exercises_ref
            .where("date", ">=", datetime.combine(day, datetime.min.time()))
            .where("date", "<", datetime.combine(day + timedelta(days=1), datetime.min.time()))
            .stream()
        )
    else:
        docs = exercises_ref.stream()

    exercises = []
    for doc in docs:
        data = doc.to_dict()
        exercise = Exercise(
            date=data.get("date"),
            name=data.get("name"),
            reps=data.get("reps"),
            duration=data.get("duration"),
            unit=data.get("unit"),
        )
        exercises.append(exercise)

    return exercises

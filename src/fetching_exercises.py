from datetime import date, datetime, timedelta
from typing import List

from src.dtos import ExerciseDay, ExerciseEntry


def fetch_exercises(db, day: date = None) -> List[ExerciseEntry]:
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
        exercise = ExerciseEntry(
            date=data.get("date"),
            name=data.get("name"),
            reps=data.get("reps"),
            duration=data.get("duration"),
            unit=data.get("unit"),
        )
        exercises.append(exercise)

    return exercises


def sum_exercises(exercises: List[ExerciseEntry]) -> List[ExerciseDay]:
    summed = {}
    for exercise in exercises:
        key = (exercise.date.date(), exercise.name)
        if key not in summed:
            summed[key] = ExerciseDay(
                date=exercise.date.date(),
                name=exercise.name,
                reps=0,
                duration=0,
                unit=exercise.unit,
            )
        if exercise.reps:
            summed[key].reps += exercise.reps
        if exercise.duration:
            summed[key].duration += exercise.duration
        if exercise.unit:
            summed[key].unit = exercise.unit

    return list(summed.values())
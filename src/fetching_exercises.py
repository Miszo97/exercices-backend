from datetime import date, datetime, timedelta
from typing import List
from .dtos import (
    RepsExerciseEntry,
    DurationExerciseEntry,
    RepsExerciseDaySum,
    DurationExerciseDaySum,
    ExerciseEntryAbstract,
    ExerciseDaySumAbstract,
)


def fetch_exercises(db, day: date = None) -> List[ExerciseEntryAbstract]:
    exercises_ref = db.collection("exercises").order_by("date")

    if day:
        docs = (
            exercises_ref.where(
                "date", ">=", datetime.combine(day, datetime.min.time())
            )
            .where(
                "date",
                "<",
                datetime.combine(day + timedelta(days=1), datetime.min.time()),
            )
            .stream()
        )
    else:
        docs = exercises_ref.stream()

    exercises: List[ExerciseEntryAbstract] = []
    for doc in docs:
        data = doc.to_dict()
        name = data.get("name")
        dt = data.get("date")
        reps = data.get("reps")
        duration = data.get("duration")
        unit = data.get("unit")
        if reps is not None:
            exercises.append(RepsExerciseEntry(date=dt, name=name, reps=reps))
        elif duration is not None:
            exercises.append(
                DurationExerciseEntry(date=dt, name=name, duration=duration, unit=unit)
            )
        else:
            continue

    return exercises


def sum_exercises(
    exercises: List[ExerciseEntryAbstract],
) -> List[ExerciseDaySumAbstract]:
    summed: dict[tuple[date, str, type], ExerciseDaySumAbstract] = {}
    order: list[tuple[date, str, type]] = []

    for exercise in exercises:
        if not isinstance(exercise, (RepsExerciseEntry, DurationExerciseEntry)):
            continue
        key = (exercise.date.date(), exercise.name, type(exercise))
        if key not in summed:
            if isinstance(exercise, RepsExerciseEntry):
                summed[key] = RepsExerciseDaySum(
                    date=exercise.date.date(), name=exercise.name, reps=0
                )
            else:
                summed[key] = DurationExerciseDaySum(
                    date=exercise.date.date(),
                    name=exercise.name,
                    duration=0,
                    unit=exercise.unit,
                )
            order.append(key)

        if isinstance(exercise, RepsExerciseEntry):
            summed[key].reps += exercise.reps
        else:
            summed[key].duration += exercise.duration
            if exercise.unit is not None:
                summed[key].unit = exercise.unit

    return [summed[k] for k in order]

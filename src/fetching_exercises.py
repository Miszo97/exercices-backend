from datetime import date
from typing import List

from src.dtos import (
    DurationExerciseDaySum,
    DurationExerciseEntry,
    ExerciseDaySumAbstract,
    ExerciseEntryAbstract,
    ExercisesDaySumOutput,
    RepsExerciseDaySum,
    RepsExerciseEntry,
)


def sum_exercises(
    exercises: List[ExerciseEntryAbstract],
) -> ExercisesDaySumOutput:
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
                )
            order.append(key)

        if isinstance(exercise, RepsExerciseEntry):
            summed[key].reps += exercise.reps
        else:
            summed[key].duration += exercise.duration

    return ExercisesDaySumOutput(exercises=[summed[k] for k in order])

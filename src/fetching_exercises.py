from datetime import date
from typing import List, TypeAlias, TypeGuard

from src.dtos import (
    DurationExerciseEntry,
    DurationExerciseDaySum,
    ExerciseDaySumAbstract,
    ExerciseEntryAbstract,
    ExercisesDaySumOutput,
    RepsExerciseDaySum,
    RepsExerciseEntry,
)


SupportedExerciseEntry: TypeAlias = RepsExerciseEntry | DurationExerciseEntry
ExerciseSumKey: TypeAlias = tuple[date, str, type[ExerciseEntryAbstract]]


def _is_supported_exercise(
        exercise: ExerciseEntryAbstract,
) -> TypeGuard[SupportedExerciseEntry]:
    return isinstance(exercise, (RepsExerciseEntry, DurationExerciseEntry))


def _exercise_sum_key(exercise: SupportedExerciseEntry) -> ExerciseSumKey:
    return exercise.date.date(), exercise.name, type(exercise)


def _empty_day_sum_for(exercise: SupportedExerciseEntry) -> ExerciseDaySumAbstract:
    exercise_date = exercise.date.date()

    if isinstance(exercise, RepsExerciseEntry):
        return RepsExerciseDaySum(date=exercise_date, name=exercise.name, reps=0)

    return DurationExerciseDaySum(
        date=exercise_date,
        name=exercise.name,
        duration=0,
    )


def _add_to_day_sum(
        day_sum: ExerciseDaySumAbstract,
        exercise: SupportedExerciseEntry,
) -> None:
    if isinstance(exercise, RepsExerciseEntry) and isinstance(day_sum, RepsExerciseDaySum):
        day_sum.reps = (day_sum.reps or 0) + exercise.reps
        return

    if isinstance(exercise, DurationExerciseEntry) and isinstance(
        day_sum, DurationExerciseDaySum
    ):
        day_sum.duration = (day_sum.duration or 0) + exercise.duration
        return

    raise TypeError("Exercise entry and day sum types do not match")


def sum_exercises(
        exercises: List[ExerciseEntryAbstract],
) -> ExercisesDaySumOutput:
    summed: dict[ExerciseSumKey, ExerciseDaySumAbstract] = {}
    order: list[ExerciseSumKey] = []

    for exercise in exercises:
        if not _is_supported_exercise(exercise):
            continue

        key = _exercise_sum_key(exercise)

        if key not in summed:
            summed[key] = _empty_day_sum_for(exercise)
            order.append(key)

        _add_to_day_sum(summed[key], exercise)

    return ExercisesDaySumOutput(exercises=[summed[key] for key in order])

import collections
from datetime import datetime, timedelta
from typing import List

from dtos import DurationExerciseEntry, ExerciseEntryAbstract, RepsExerciseEntry


def ordered_set(iterable):
    return list(collections.OrderedDict.fromkeys(iterable))


def get_table_data(exercises: List[ExerciseEntryAbstract]):
    if not exercises:
        return [], []

    exercise_names = list(dict.fromkeys((exercise.name for exercise in exercises)))

    grouped_by_date: dict[str, dict[str, dict[str, object]]] = {}
    for exercise in exercises:
        date_str = exercise.date.strftime("%Y-%m-%d")
        grouped_by_date.setdefault(
            date_str,
            {name: {"reps": 0, "duration": 0, "unit": ""} for name in exercise_names},
        )
        if isinstance(exercise, RepsExerciseEntry):
            grouped_by_date[date_str][exercise.name]["reps"] += exercise.reps
        elif isinstance(exercise, DurationExerciseEntry):
            grouped_by_date[date_str][exercise.name]["duration"] += exercise.duration
            grouped_by_date[date_str][exercise.name]["unit"] = exercise.unit or ""

    if not grouped_by_date:
        return exercise_names, []

    first_date = min(datetime.strptime(date, "%Y-%m-%d") for date in grouped_by_date)
    today = datetime.now()
    current_date = first_date
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        grouped_by_date.setdefault(
            date_str,
            {name: {"reps": 0, "duration": 0, "unit": ""} for name in exercise_names},
        )
        current_date += timedelta(days=1)

    rows = [
        [
            date,
            [
                str(data[name]["reps"])
                if data[name]["reps"]
                else f"{data[name]['duration']} {data[name]['unit']}".strip()
                for name in exercise_names
            ],
        ]
        for date, data in sorted(grouped_by_date.items())
    ]

    return exercise_names, rows

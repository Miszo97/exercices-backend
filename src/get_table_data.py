# ordered set
import collections
from datetime import datetime, timedelta
from typing import List

from src.dtos import ExerciseEntry


def ordered_set(iterable):
    return list(collections.OrderedDict.fromkeys(iterable))


def get_table_data(exercises: List[ExerciseEntry]):
    exercise_names = list(dict.fromkeys((exercise.name for exercise in exercises)))

    grouped_by_date = {}
    for exercise in exercises:
        date_str = exercise.date.strftime("%Y-%m-%d")
        grouped_by_date.setdefault(
            date_str,
            {name: {"reps": 0, "duration": 0, "unit": ""} for name in exercise_names},
        )
        grouped_by_date[date_str][exercise.name]["reps"] += exercise.reps or 0
        grouped_by_date[date_str][exercise.name]["duration"] += exercise.duration or 0
        grouped_by_date[date_str][exercise.name]["unit"] = exercise.unit or ""

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

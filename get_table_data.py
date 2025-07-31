from typing import List
from datetime import datetime, timedelta
from dtos import Exercise


def get_exercise_names_by_priority(exercises: List[Exercise], priority_map: dict):
    return sorted(
        {exercise.name for exercise in exercises},
        key=lambda name: priority_map.get(name, 0),
        reverse=True
    )

priority_map = {
    "abs one leg kick": 2,
    "band exterior bottom": 9,
    "band exterior top": 8,
    "biceps curls": 1,
    "both legs foam stabilization": 10,
    "copenhagen adduction": 7,
    "glutes one leg up": 6,
    "plank": 6,
    "plank both sides": 5,
    "push ups": 1
}

def get_table_data(exercises: List[Exercise]):
    exercise_names = get_exercise_names_by_priority(exercises=exercises, priority_map=priority_map)

    grouped_by_date = {}
    for exercise in exercises:
        date_str = exercise.date.strftime('%Y-%m-%d')
        grouped_by_date.setdefault(date_str, {name: {"reps": 0, "duration": 0, "unit": ""} for name in exercise_names})
        grouped_by_date[date_str][exercise.name]["reps"] += exercise.reps or 0
        grouped_by_date[date_str][exercise.name]["duration"] += exercise.duration or 0
        grouped_by_date[date_str][exercise.name]["unit"] = exercise.unit or ""

    first_date = min(datetime.strptime(date, '%Y-%m-%d') for date in grouped_by_date)
    today = datetime.now()
    current_date = first_date
    while current_date <= today:
        date_str = current_date.strftime('%Y-%m-%d')
        grouped_by_date.setdefault(date_str, {name: {"reps": 0, "duration": 0, "unit": ""} for name in exercise_names})
        current_date += timedelta(days=1)

    rows = [
        [date, [str(data[name]["reps"]) if data[name]["reps"] else f"{data[name]['duration']} {data[name]['unit']}".strip()
                for name in exercise_names]]
        for date, data in sorted(grouped_by_date.items())
    ]

    return exercise_names, rows
from datetime import datetime, timedelta
from typing import List, Tuple

from src.dtos import ExerciseEntryAbstract, RepsExerciseEntry, dfs
from src.utils import convert_seconds_to_minutes_format


def _format_exercise_cell(exercise_data: dict) -> str:
    """Helper to format a single table cell based on reps/duration."""
    if exercise_data["reps"]:
        return str(exercise_data["reps"])
    if exercise_data["duration"]:
        return convert_seconds_to_minutes_format(seconds=exercise_data["duration"])
    return ""


def get_table_data(
    exercises: List[ExerciseEntryAbstract],
) -> Tuple[List[str], List[list]]:
    if not exercises:
        return [], []

    # 1. Extract unique exercise names
    exercise_names = list(dict.fromkeys(exercise.name for exercise in exercises))

    # 2. Normalize dates to avoid timezone/time issues
    first_date = min(e.date for e in exercises)
    if isinstance(first_date, datetime):
        first_date = first_date.date()

    today = datetime.now().date()
    current_date = first_date

    # 3. Pre-fill the dictionary with all dates up to today
    grouped_by_date: dict[str, dict[str, dict[str, int]]] = {}

    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        grouped_by_date[date_str] = {
            name: {"reps": 0, "duration": 0} for name in exercise_names
        }
        current_date += timedelta(days=1)

    # 4. Populate the data
    for exercise in exercises:
        date_str = exercise.date.strftime("%Y-%m-%d")

        # In case an exercise date is somehow in the future beyond `today`
        if date_str not in grouped_by_date:
            grouped_by_date[date_str] = {
                name: {"reps": 0, "duration": 0} for name in exercise_names
            }

        if isinstance(exercise, RepsExerciseEntry):
            grouped_by_date[date_str][exercise.name]["reps"] += exercise.reps
        elif isinstance(exercise, dfs):
            grouped_by_date[date_str][exercise.name]["duration"] += exercise.duration

    # 5. Format the rows
    rows = []
    for date_str, data in sorted(grouped_by_date.items()):
        row_cells = [_format_exercise_cell(data[name]) for name in exercise_names]
        rows.append([date_str, row_cells])

    return exercise_names, rows

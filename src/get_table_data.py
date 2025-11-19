import collections
from datetime import datetime, timedelta
from typing import List

from src.dtos import DurationExerciseEntry, ExerciseEntryAbstract, RepsExerciseEntry
from src.utils import convert_seconds_to_minutes_format


def ordered_set(iterable):
    return list(collections.OrderedDict.fromkeys(iterable))


from datetime import datetime, timedelta, date
from collections import defaultdict
from typing import List, Tuple, Any


# Assuming these imports exist in your project context
# from models import ExerciseEntryAbstract, RepsExerciseEntry, DurationExerciseEntry
# from utils import convert_seconds_to_minutes_format

def get_table_data(exercises: List[ExerciseEntryAbstract]) -> Tuple[List[str], List[List[Any]]]:
    if not exercises:
        return [], []

    # 1. Extract unique exercise names while preserving order
    exercise_names = list(dict.fromkeys(e.name for e in exercises))

    # 2. Group data: {(date, exercise_name): {'reps': 0, 'duration': 0}}
    # Using defaultdict avoids manual initialization checks
    daily_totals = defaultdict(lambda: {"reps": 0, "duration": 0})

    # Track min_date found in data to start the table
    dates = [e.date.date() if isinstance(e.date, datetime) else e.date for e in exercises]
    min_date = min(dates) if dates else date.today()

    for exercise in exercises:
        # Normalize to date object to ignore time components
        entry_date = exercise.date.date() if isinstance(exercise.date, datetime) else exercise.date
        key = (entry_date, exercise.name)

        if isinstance(exercise, RepsExerciseEntry):
            daily_totals[key]["reps"] += exercise.reps
        elif isinstance(exercise, DurationExerciseEntry):
            daily_totals[key]["duration"] += exercise.duration

    # 3. Generate Rows (Iterate from first date to today)
    rows = []
    current_date = min_date
    today = date.today()

    while current_date <= today:
        row_data = [current_date.strftime("%Y-%m-%d")]

        for name in exercise_names:
            stats = daily_totals.get((current_date, name))

            if not stats:
                row_data.append("")
                continue

            # Formatting Logic
            if stats["reps"] > 0:
                val = str(stats["reps"])
            elif stats["duration"] > 0:
                val = convert_seconds_to_minutes_format(seconds=stats["duration"])
            else:
                val = ""

            row_data.append(val)

        rows.append(row_data)
        current_date += timedelta(days=1)

    return exercise_names, rows

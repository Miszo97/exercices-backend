from datetime import datetime

import pytz


def add_exercise(name, db, reps=None, duration=None, unit=None):
    exercises_ref = db.collection("exercises")
    data = {}
    if reps is not None:
        data["reps"] = reps
    if duration is not None:
        data["duration"] = duration
    if unit is not None:
        data["unit"] = unit

    cest = pytz.timezone("Europe/Warsaw")
    current_time = datetime.now(cest)

    if name is None:
        raise Exception("name is required")

    data["date"] = current_time
    data["name"] = name
    exercises_ref.add(data)

    return data

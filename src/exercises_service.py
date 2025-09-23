from datetime import datetime

import pytz


class ExerciseService:
    """Service that handles exercise persistence; db is injected via __init__."""

    def __init__(self, db):
        self.db = db

    def _now_warsaw(self):
        cest = pytz.timezone("Europe/Warsaw")
        return datetime.now(cest)

    def add_reps_exercise(self, name, reps, unit=None):
        """
        Adds a repetitions-based exercise entry with an explicit type field.
        Leaves add_exercise intact by independently writing the document.
        """
        exercises_ref = self.db.collection("exercises")
        if name is None:
            raise Exception("name is required")
        if reps is None:
            raise Exception("reps is required")

        current_time = self._now_warsaw()
        data = {
            "date": current_time,
            "name": name,
            "reps": reps,
            "type": "reps",
        }
        if unit is not None:
            data["unit"] = unit

        exercises_ref.add(data)
        return data

    def add_duration_exercise(self, name, duration, unit="seconds"):
        """
        Adds a duration-based exercise entry with an explicit type field.
        Leaves add_exercise intact by independently writing the document.
        """
        exercises_ref = self.db.collection("exercises")
        if name is None:
            raise Exception("name is required")
        if duration is None:
            raise Exception("duration is required")

        current_time = self._now_warsaw()
        data = {
            "date": current_time,
            "name": name,
            "duration": duration,
            "type": "duration",
        }
        if unit is not None:
            data["unit"] = unit

        exercises_ref.add(data)
        return data

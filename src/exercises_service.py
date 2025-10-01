from datetime import date, datetime, timedelta
from typing import List

import firebase_admin
import pytz
from firebase_admin import firestore

from src.dtos import DurationExerciseEntry, ExerciseEntryAbstract, RepsExerciseEntry


class ExerciseService:
    """Service that handles exercise persistence; db is injected via __init__."""

    def __init__(self):
        firebase_admin.initialize_app()
        db = firestore.client()
        self.db = db

    @staticmethod
    def _now_warsaw():
        cest = pytz.timezone("Europe/Warsaw")
        return datetime.now(cest)

    def add_reps_exercise(self, name, reps, unit=None):
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

    def fetch_exercises(self, day: date = None) -> List[ExerciseEntryAbstract]:
        exercises_ref = self.db.collection("exercises").order_by("date")

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
                    DurationExerciseEntry(
                        date=dt, name=name, duration=duration, unit=unit
                    )
                )
            else:
                continue

        return exercises

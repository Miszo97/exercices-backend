from datetime import date, datetime, timedelta
from typing import List

import firebase_admin
from firebase_admin import firestore

from dtos import DurationExerciseEntry, ExerciseEntryAbstract, RepsExerciseEntry
from exercises_sources.dtos import AddDurationExercisesRequest, AddRepsExercisesRequest
from exercises_sources.exercises_source import ExerciseSource


class FirebaseExerciseSource(ExerciseSource):
    """Concrete implementation of ExerciseSource using Firebase Firestore."""

    def __init__(self):
        firebase_admin.initialize_app()
        db = firestore.client()
        self.db = db

    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        exercises_ref = self.db.collection("exercises")

        current_time = self._now_warsaw()
        data = {
            "date": current_time,
            "name": request.name,
            "reps": request.reps,
            "type": "reps",
        }
        if request.unit is not None:
            data["unit"] = request.unit

        exercises_ref.add(data)
        return data

    def add_duration_exercise(self, request: AddDurationExercisesRequest):
        exercises_ref = self.db.collection("exercises")

        current_time = self._now_warsaw()
        data = {
            "date": current_time,
            "name": request.name,
            "duration": request.duration,
            "type": "duration",
        }
        if request.unit is not None:
            data["unit"] = request.unit

        exercises_ref.add(data)
        return data

    def fetch_exercises(
        self, day: date = None, limit=None, offset=None
    ) -> List[ExerciseEntryAbstract]:
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

        if offset is not None:
            exercises = exercises[offset:]
        if limit is not None:
            exercises = exercises[:limit]

        return exercises

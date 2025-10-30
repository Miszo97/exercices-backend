from datetime import date, datetime, timedelta
from typing import List

import firebase_admin
import pytz
from firebase_admin import firestore

from src.dtos import DurationExerciseEntry, ExerciseEntryAbstract, RepsExerciseEntry
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.exercises_sources.exercises_source import ExerciseSource


class FirebaseExerciseSource(ExerciseSource):
    """Concrete implementation of ExerciseSource using Firebase Firestore."""

    def __init__(self):
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()
        db = firestore.client()
        self.db = db

    @staticmethod
    def _now_warsaw():
        cest = pytz.timezone("Europe/Warsaw")
        return datetime.now(cest)

    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        exercises_ref = self.db.collection("exercises")

        current_time = self._now_warsaw()
        data = {
            "date": current_time,
            "name": request.name,
            "reps": request.reps,
            "type": "reps",
        }

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

        exercises_ref.add(data)
        return data

    def fetch_exercises(
        self, day: date = None, limit=None, offset=None, last_days: int = None
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
        elif last_days is not None:
            now = datetime.now()
            start_date = now - timedelta(days=last_days)
            docs = (
                exercises_ref.where("date", ">=", start_date)
                .where("date", "<=", now)
                .stream()
            )
        else:
            docs = exercises_ref.stream()

        exercises: List[ExerciseEntryAbstract] = []
        for doc in docs:
            data = doc.to_dict()
            ex_name = data.get("name")
            dt = data.get("date")
            reps = data.get("reps")
            duration = data.get("duration")
            if reps is not None:
                exercises.append(RepsExerciseEntry(date=dt, name=ex_name, reps=reps))
            elif duration is not None:
                exercises.append(
                    DurationExerciseEntry(date=dt, name=ex_name, duration=duration)
                )
            else:
                continue

        if offset is not None:
            exercises = exercises[offset:]
        if limit is not None:
            exercises = exercises[:limit]

        return exercises

    def fetch_exercises_by_name(
        self,
        name: str,
        day: date = None,
        limit: int | None = None,
        offset: int | None = None,
        last_days: int | None = None,
    ) -> List[ExerciseEntryAbstract]:
        exercises_ref = (
            self.db.collection("exercises").order_by("date").where("name", "==", name)
        )

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
        elif last_days is not None:
            now = datetime.now()
            start_date = now - timedelta(days=last_days)
            docs = (
                exercises_ref.where("date", ">=", start_date)
                .where("date", "<=", now)
                .stream()
            )
        else:
            docs = exercises_ref.stream()

        exercises: List[ExerciseEntryAbstract] = []
        for doc in docs:
            data = doc.to_dict()
            ex_name = data.get("name")
            dt = data.get("date")
            reps = data.get("reps")
            duration = data.get("duration")
            if reps is not None:
                exercises.append(RepsExerciseEntry(date=dt, name=ex_name, reps=reps))
            elif duration is not None:
                exercises.append(
                    DurationExerciseEntry(date=dt, name=ex_name, duration=duration)
                )
            else:
                continue

        if offset is not None:
            exercises = exercises[offset:]
        if limit is not None:
            exercises = exercises[:limit]

        return exercises

from datetime import date
from typing import List

from exercises_sources.firebase_exercises_source import FirebaseExerciseSource
from src.dtos import ExerciseEntryAbstract


class ExerciseService:
    def __init__(self, exercise_source: ExerciseSource = None):
        if exercise_source is None:
            self.exercise_source = FirebaseExerciseSource()
        else:
            self.exercise_source = exercise_source

    def add_reps_exercise(self, name, reps, unit=None):
        return self.exercise_source.add_reps_exercise(name, reps, unit)

    def add_duration_exercise(self, name, duration, unit="seconds"):
        return self.exercise_source.add_duration_exercise(name, duration, unit)

    def fetch_exercises(self, day: date = None) -> List[ExerciseEntryAbstract]:
        return self.exercise_source.fetch_exercises(day)

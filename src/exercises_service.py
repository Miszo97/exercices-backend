from datetime import date
from typing import List

from dtos import ExerciseEntryAbstract
from exercises_sources.dtos import AddDurationExercisesRequest, AddRepsExercisesRequest
from exercises_sources.exercises_source import ExerciseSource
from exercises_sources.firebase.firebase_exercises_source import FirebaseExerciseSource


class ExerciseService:
    def __init__(self, exercise_source: ExerciseSource = None):
        if exercise_source is None:
            self.exercise_source = FirebaseExerciseSource()
        else:
            self.exercise_source = exercise_source

    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        return self.exercise_source.add_reps_exercise(request=request)

    def add_duration_exercise(self, request: AddDurationExercisesRequest):
        return self.exercise_source.add_duration_exercise(request=request)

    def fetch_exercises(
        self, day: date = None, limit: int = 10, offset: int = 0, last_days: int = None
    ) -> List[ExerciseEntryAbstract]:
        return self.exercise_source.fetch_exercises(
            day=day, limit=limit, offset=offset, last_days=last_days
        )

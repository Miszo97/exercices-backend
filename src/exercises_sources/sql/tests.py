from datetime import date, datetime, timedelta

from src.database_models import DurationExerciseEntry, RepsExerciseEntry
from src.dtos import DurationExerciseStats, RepsExerciseStats
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.exercises_sources.sql import SQLExerciseSource

source = SQLExerciseSource()


class TestSQLExerciseSource:
    def test_fetch_exercises_for_today(self, session):
        source.add_duration_exercise(
            AddDurationExercisesRequest(name="plank", duration=30)
        )
        source.add_duration_exercise(
            AddDurationExercisesRequest(name="plank", duration=45)
        )

        results = source.fetch_exercises(day=date.today())
        assert isinstance(results, list)
        for entry in results:
            assert entry.date.date() == date.today()

    def test_sum_exercises_for_day(self, session):
        session.add_all(
            [
                DurationExerciseEntry(date=datetime.now(), name="plank", duration=60),
                DurationExerciseEntry(date=datetime.now(), name="plank", duration=60),
                DurationExerciseEntry(
                    date=datetime.now() - timedelta(days=1), name="plank", duration=60
                ),
                RepsExerciseEntry(date=datetime.now(), name="push ups", reps=20),
                RepsExerciseEntry(date=datetime.now(), name="push ups", reps=20),
                RepsExerciseEntry(
                    date=datetime.now() - timedelta(days=1), name="push ups", reps=20
                ),
                RepsExerciseEntry(
                    date=datetime.now() - timedelta(days=1), name="push ups", reps=20
                ),
            ]
        )
        session.commit()

        results = source.sum_exercises_for_day(day=date.today())
        assert results == {"plank": 120, "push ups": 40}


def test_a(session):
    source.add_duration_exercise(AddDurationExercisesRequest(name="test", duration=10))
    data = source.fetch_exercises()
    assert len(data) == 1


def test_get_exercise_stats_duration(session):
    # Arrange: add multiple duration entries for the same exercise name
    source.add_duration_exercise(AddDurationExercisesRequest(name="plank", duration=30))
    source.add_duration_exercise(AddDurationExercisesRequest(name="plank", duration=45))

    # Act
    stats = source.get_exercise_stats(name="plank")

    # Assert
    assert isinstance(stats, DurationExerciseStats)
    assert stats.total_duration == 75


def test_get_exercise_stats_reps(session):
    # Arrange: add multiple reps entries for the same exercise name
    source.add_reps_exercise(AddRepsExercisesRequest(name="pushup", reps=10))
    source.add_reps_exercise(AddRepsExercisesRequest(name="pushup", reps=15))

    # Act
    stats = source.get_exercise_stats(name="pushup")

    # Assert
    assert isinstance(stats, RepsExerciseStats)
    assert stats.total_reps == 25


def test_get_exercise_stats_reps_priority_over_duration(session):
    # Arrange: add both reps and duration entries for the same name
    source.add_reps_exercise(AddRepsExercisesRequest(name="burpee", reps=10))
    source.add_duration_exercise(
        AddDurationExercisesRequest(name="burpee", duration=60)
    )

    # Act
    stats = source.get_exercise_stats(name="burpee")

    # Assert: per implementation, reps are prioritized if present
    assert isinstance(stats, RepsExerciseStats)
    assert stats.total_reps == 10


def test_get_exercise_stats_no_entries(session):
    # Act
    stats = source.get_exercise_stats(name="unknown_exercise")

    # Assert: should return RepsExerciseStats with total_reps=None when no entries
    assert isinstance(stats, RepsExerciseStats)
    assert stats.total_reps is None

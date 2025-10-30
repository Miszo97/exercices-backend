from datetime import date, timedelta

import pytest

from src.database_models import Base, get_engine
from src.dtos import DurationExerciseStats, RepsExerciseStats
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.exercises_sources.sql import SQLExerciseSource

source = SQLExerciseSource()
from sqlalchemy import create_engine


class TestSQLExerciseSource:
    @pytest.mark.parametrize(
        "test_day",
        [
            date.today(),
            date.today() - timedelta(days=1),
            date.today() - timedelta(days=7),
        ],
    )
    def test_fetch_exercises_for_various_days(self, test_day):
        results = source.fetch_exercises(day=test_day)
        assert isinstance(results, list)
        for entry in results:
            assert entry.date.date() == test_day

    def test_fetch_exercises_for_last_5_days(self):
        results = source.fetch_exercises(last_days=5)
        assert isinstance(results, list)
        cutoff_date = date.today() - timedelta(days=5)
        for entry in results:
            assert entry.date.date() >= cutoff_date


@pytest.fixture()
def db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_a(db):
    source.add_duration_exercise(AddDurationExercisesRequest(name="test", duration=10))
    data = source.fetch_exercises()
    assert len(data) == 1


def test_get_exercise_stats_duration(db):
    # Arrange: add multiple duration entries for the same exercise name
    source.add_duration_exercise(AddDurationExercisesRequest(name="plank", duration=30))
    source.add_duration_exercise(AddDurationExercisesRequest(name="plank", duration=45))

    # Act
    stats = source.get_exercise_stats(name="plank")

    # Assert
    assert isinstance(stats, DurationExerciseStats)
    assert stats.total_duration == 75


def test_get_exercise_stats_reps(db):
    # Arrange: add multiple reps entries for the same exercise name
    source.add_reps_exercise(AddRepsExercisesRequest(name="pushup", reps=10))
    source.add_reps_exercise(AddRepsExercisesRequest(name="pushup", reps=15))

    # Act
    stats = source.get_exercise_stats(name="pushup")

    # Assert
    assert isinstance(stats, RepsExerciseStats)
    assert stats.total_reps == 25


def test_get_exercise_stats_reps_priority_over_duration(db):
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


def test_get_exercise_stats_no_entries(db):
    # Act
    stats = source.get_exercise_stats(name="unknown_exercise")

    # Assert: should return RepsExerciseStats with total_reps=None when no entries
    assert isinstance(stats, RepsExerciseStats)
    assert stats.total_reps is None

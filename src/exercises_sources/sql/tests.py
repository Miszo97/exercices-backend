from datetime import date, timedelta

import pytest

from exercises_sources.dtos import AddDurationExercisesRequest
from src.database_models import Base, get_engine
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

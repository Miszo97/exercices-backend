from datetime import date, timedelta

import pytest

from src.exercises_sources.sql import SQLExerciseSource

source = SQLExerciseSource()


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

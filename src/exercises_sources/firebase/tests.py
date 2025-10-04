from datetime import date, timedelta

import pytest

from exercises_sources.firebase.firebase_exercises_source import (
    FirebaseExerciseSource,
)

source = FirebaseExerciseSource()


class TestFirebaseExerciseSource:
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

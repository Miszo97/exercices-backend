from datetime import date, datetime, timedelta
from typing import Dict, List

import pytz
from sqlalchemy import Date, and_, cast, func, select
from sqlalchemy.orm import Session, sessionmaker

from src.database_models import (
    DurationExerciseEntry as DurationExerciseModel,
)
from src.database_models import (
    RepsExerciseEntry as RepsExerciseModel,
)
from src.database_models import (
    get_engine,
)
from src.dtos import (
    DurationExerciseStats,
    ExerciseEntryAbstract,
    RepsExerciseEntry,
    RepsExerciseStats,
)
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.exercises_sources.exercises_source import ExerciseSource


class SQLExerciseSource(ExerciseSource):
    """Concrete implementation of ExerciseSource using SQLAlchemy models."""

    def __init__(self, get_engine_method=get_engine):
        # Prepare a session factory
        self.engine = get_engine_method()
        self._SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False
        )

    @staticmethod
    def _now_warsaw():
        cest = pytz.timezone("Europe/Warsaw")
        return datetime.now(cest)

    def _session(self) -> Session:
        return self._SessionLocal()

    def add_reps_exercise(self, request: AddRepsExercisesRequest):
        current_time = self._now_warsaw()
        with self._session() as session:
            model = RepsExerciseModel(
                date=current_time, name=request.name, reps=request.reps
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return {
                "id": model.id,
                "date": model.date,
                "name": model.name,
                "reps": model.reps,
                "type": "reps",
            }

    def add_duration_exercise(self, request: AddDurationExercisesRequest):
        current_time = self._now_warsaw()
        with self._session() as session:
            model = DurationExerciseModel(
                date=current_time,
                name=request.name,
                duration=request.duration,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return {
                "id": model.id,
                "date": model.date,
                "name": model.name,
                "duration": model.duration,
                "type": "duration",
            }

    def sum_exercises_for_day(self, day: date = None) -> Dict[str, int]:
        with self._session() as session:
            duration_response = (
                session.query(
                    DurationExerciseModel.name, func.sum(DurationExerciseModel.duration)
                )
                .where(func.DATE(DurationExerciseModel.date) == day)
                .group_by(DurationExerciseModel.name)
                .all()
            )

            reps_response = (
                session.query(RepsExerciseModel.name, func.sum(RepsExerciseModel.reps))
                .where(func.DATE(RepsExerciseModel.date) == day)
                .group_by(RepsExerciseModel.name)
                .all()
            )

            return {key: val for key, val in reps_response + duration_response}

    def fetch_exercises(
        self, day: date = None, limit=None, offset=None, last_days: int = None
    ) -> List[ExerciseEntryAbstract]:
        with self._session() as session:
            # Build filters
            start_dt = end_dt = None
            if day:
                day_date = (
                    day
                    if isinstance(day, date) and not isinstance(day, datetime)
                    else day.date()
                )
                start_dt = datetime.combine(day_date, datetime.min.time())
                end_dt = datetime.combine(
                    day_date + timedelta(days=1), datetime.min.time()
                )
            elif last_days is not None:
                now = datetime.now()
                start_dt = now - timedelta(days=last_days)
                end_dt = now

            reps_stmt = select(RepsExerciseModel)
            dur_stmt = select(DurationExerciseModel)
            if start_dt is not None and end_dt is not None:
                reps_stmt = reps_stmt.where(
                    and_(
                        RepsExerciseModel.date >= start_dt,
                        RepsExerciseModel.date < end_dt,
                    )
                )
                dur_stmt = dur_stmt.where(
                    and_(
                        DurationExerciseModel.date >= start_dt,
                        DurationExerciseModel.date < end_dt,
                    )
                )

            reps_rows = session.execute(reps_stmt).scalars().all()
            dur_rows = session.execute(dur_stmt).scalars().all()

            exercises: List[ExerciseEntryAbstract] = []
            for r in reps_rows:
                exercises.append(
                    RepsExerciseEntry(date=r.date, name=r.name, reps=r.reps)
                )
            for d in dur_rows:
                exercises.append(
                    DurationExerciseEntry(date=d.date, name=d.name, duration=d.duration)
                )

            exercises.sort(key=lambda x: x.date)

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
        with self._session() as session:
            start_dt = end_dt = None
            if day:
                day_date = (
                    day
                    if isinstance(day, date) and not isinstance(day, datetime)
                    else day.date()
                )
                start_dt = datetime.combine(day_date, datetime.min.time())
                end_dt = datetime.combine(
                    day_date + timedelta(days=1), datetime.min.time()
                )
            elif last_days is not None:
                now = datetime.now()
                start_dt = now - timedelta(days=last_days)
                end_dt = now

            reps_stmt = select(RepsExerciseModel).where(RepsExerciseModel.name == name)
            dur_stmt = select(DurationExerciseModel).where(
                DurationExerciseModel.name == name
            )

            if start_dt is not None and end_dt is not None:
                reps_stmt = reps_stmt.where(
                    and_(
                        RepsExerciseModel.date >= start_dt,
                        RepsExerciseModel.date < end_dt,
                    )
                )
                dur_stmt = dur_stmt.where(
                    and_(
                        DurationExerciseModel.date >= start_dt,
                        DurationExerciseModel.date < end_dt,
                    )
                )

            reps_rows = session.execute(reps_stmt).scalars().all()
            dur_rows = session.execute(dur_stmt).scalars().all()

            exercises: List[ExerciseEntryAbstract] = []
            for r in reps_rows:
                exercises.append(
                    RepsExerciseEntry(date=r.date, name=r.name, reps=r.reps)
                )
            for d in dur_rows:
                exercises.append(
                    DurationExerciseEntry(date=d.date, name=d.name, duration=d.duration)
                )

            exercises.sort(key=lambda x: x.date, reverse=True)

            if offset is not None:
                exercises = exercises[offset:]
            if limit is not None:
                exercises = exercises[:limit]

            return exercises

    def get_exercise_stats(
        self, name: str
    ) -> RepsExerciseStats | DurationExerciseStats:
        # Compute aggregate stats for a given exercise name.
        # If there are reps-based entries with this name, return RepsExerciseStats.
        # Otherwise, if there are duration-based entries, return DurationExerciseStats.
        # If none exist, return an empty RepsExerciseStats with total_reps=None.
        with self._session() as session:
            # Sum reps for the given name (all time)
            reps_total = session.execute(
                select(func.sum(RepsExerciseModel.reps)).where(
                    RepsExerciseModel.name == name
                )
            ).scalar()

            if reps_total is not None:
                # Also compute sum for the last 30 days
                now = self._now_warsaw()
                start_30 = now - timedelta(days=30)
                reps_last_30 = session.execute(
                    select(func.sum(RepsExerciseModel.reps)).where(
                        and_(
                            RepsExerciseModel.name == name,
                            RepsExerciseModel.date >= start_30,
                            RepsExerciseModel.date <= now,
                        )
                    )
                ).scalar()
                return RepsExerciseStats(
                    total_reps=int(reps_total),
                    reps_in_last_30_days=int(reps_last_30)
                    if reps_last_30 is not None
                    else None,
                )

            # Sum duration for the given name (all time)
            duration_total = session.execute(
                select(func.sum(DurationExerciseModel.duration)).where(
                    DurationExerciseModel.name == name
                )
            ).scalar()

            if duration_total is not None:
                # Also compute sum for the last 30 days
                now = self._now_warsaw()
                start_30 = now - timedelta(days=30)
                duration_last_30 = session.execute(
                    select(func.sum(DurationExerciseModel.duration)).where(
                        and_(
                            DurationExerciseModel.name == name,
                            DurationExerciseModel.date >= start_30,
                            DurationExerciseModel.date <= now,
                        )
                    )
                ).scalar()
                return DurationExerciseStats(
                    total_duration=int(duration_total),
                    duration_in_last_30_days=int(duration_last_30)
                    if duration_last_30 is not None
                    else 0,
                )

            # No entries found for this name
            return RepsExerciseStats(total_reps=None)

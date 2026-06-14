from datetime import date, datetime, timedelta
from typing import Dict, List

import pytz
from sqlalchemy import Integer, and_, func, literal, select, union_all
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
    DurationExerciseEntry,
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

    @staticmethod
    def _date_range(day: date = None, last_days: int = None):
        start_dt = end_dt = None
        if day:
            day_date = (
                day if isinstance(day, date) and not isinstance(day, datetime) else day.date()
            )
            start_dt = datetime.combine(day_date, datetime.min.time())
            end_dt = datetime.combine(day_date + timedelta(days=1), datetime.min.time())
        elif last_days is not None:
            now = datetime.now()
            start_dt = now - timedelta(days=last_days)
            end_dt = now
        return start_dt, end_dt

    @staticmethod
    def _exercise_union(start_dt=None, end_dt=None, name: str | None = None):
        reps_stmt = select(
            RepsExerciseModel.id.label("id"),
            RepsExerciseModel.date.label("date"),
            RepsExerciseModel.name.label("name"),
            RepsExerciseModel.reps.label("reps"),
            literal(None, type_=Integer).label("duration"),
            literal("reps").label("type"),
            literal(0).label("type_rank"),
        )
        dur_stmt = select(
            DurationExerciseModel.id.label("id"),
            DurationExerciseModel.date.label("date"),
            DurationExerciseModel.name.label("name"),
            literal(None, type_=Integer).label("reps"),
            DurationExerciseModel.duration.label("duration"),
            literal("duration").label("type"),
            literal(1).label("type_rank"),
        )

        if name is not None:
            reps_stmt = reps_stmt.where(RepsExerciseModel.name == name)
            dur_stmt = dur_stmt.where(DurationExerciseModel.name == name)

        if start_dt is not None and end_dt is not None:
            reps_stmt = reps_stmt.where(
                and_(RepsExerciseModel.date >= start_dt, RepsExerciseModel.date < end_dt)
            )
            dur_stmt = dur_stmt.where(
                and_(
                    DurationExerciseModel.date >= start_dt,
                    DurationExerciseModel.date < end_dt,
                )
            )

        return union_all(reps_stmt, dur_stmt).subquery()

    @staticmethod
    def _to_exercise_entry(row) -> ExerciseEntryAbstract:
        if row.type == "reps":
            return RepsExerciseEntry(date=row.date, name=row.name, reps=row.reps)
        return DurationExerciseEntry(
            date=row.date, name=row.name, duration=row.duration
        )

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
            start_dt, end_dt = self._date_range(day=day, last_days=last_days)
            exercises_union = self._exercise_union(start_dt=start_dt, end_dt=end_dt)

            stmt = select(exercises_union).order_by(
                exercises_union.c.date.asc(),
                exercises_union.c.type_rank.asc(),
                exercises_union.c.id.asc(),
            )
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)

            return [self._to_exercise_entry(row) for row in session.execute(stmt)]

    def fetch_exercises_by_name(
        self,
        name: str,
        day: date = None,
        limit: int | None = None,
        offset: int | None = None,
        last_days: int | None = None,
    ) -> List[ExerciseEntryAbstract]:
        with self._session() as session:
            start_dt, end_dt = self._date_range(day=day, last_days=last_days)
            exercises_union = self._exercise_union(
                start_dt=start_dt, end_dt=end_dt, name=name
            )

            stmt = select(exercises_union).order_by(
                exercises_union.c.date.desc(),
                exercises_union.c.type_rank.asc(),
                exercises_union.c.id.asc(),
            )
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)

            return [self._to_exercise_entry(row) for row in session.execute(stmt)]

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

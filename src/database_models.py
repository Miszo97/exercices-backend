import os
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class DurationExerciseEntry(Base):
    __tablename__ = "duration_exercise_entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)


class RepsExerciseEntry(Base):
    __tablename__ = "reps_exercise_entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine

    database_url = os.getenv("DB_URI", "sqlite:///:memory:")
    connect_args = {}
    if database_url.startswith("sqlite"):
        # For SQLite, especially in-memory DBs, disable same-thread check for multithreaded use
        connect_args.setdefault("check_same_thread", False)

    if database_url.startswith("sqlite") and (
        ":memory:" in database_url or database_url.rstrip("/").endswith("sqlite://")
    ):
        _engine = create_engine(
            database_url,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
    else:
        _engine = create_engine(database_url, connect_args=connect_args)
    return _engine


def _get_session_factory():
    global _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal
    engine = get_engine()
    _SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _SessionLocal


def get_session() -> Session:
    SessionLocal = _get_session_factory()
    with SessionLocal() as session:
        yield session

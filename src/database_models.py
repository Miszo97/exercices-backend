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
from urllib.parse import quote

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

    host = os.getenv("DATABASE_HOST")
    password = os.getenv("DATABASE_PASSWORD")

    database_url = f"postgresql+psycopg://postgres:{quote(password)}@{host}:5432/postgres"
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

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

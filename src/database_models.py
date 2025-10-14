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

Base = declarative_base()


class Hero(Base):
    __tablename__ = "hero"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True)
    age: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    secret_name: Mapped[str] = mapped_column(String)


class DurationExerciseEntry(Base):
    __tablename__ = "duration_exercise_entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)


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

    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
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


def create_db_and_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_session() -> Session:
    SessionLocal = _get_session_factory()
    with SessionLocal() as session:
        yield session

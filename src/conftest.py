import pytest
from sqlalchemy.orm import Session, sessionmaker

from src.database_models import Base, get_engine
from src.exercises_sources.sql import SQLExerciseSource

source = SQLExerciseSource()


@pytest.fixture()
def session():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    yield session
    Base.metadata.drop_all(bind=engine)

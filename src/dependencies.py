import os

from fastapi import HTTPException, Request
from starlette import status

from src.exercises_service import ExerciseService
from src.exercises_sources.sql import SQLExerciseSource
from src.utils import get_hash


def get_service() -> ExerciseService:
    exercises_source = SQLExerciseSource()
    return ExerciseService(exercise_source=exercises_source)


async def check_access_key(request: Request):
    access_key = request.headers.get("Authorization")
    if not access_key:
        access_key = request.cookies.get("access_token")
    hashed = get_hash(access_key)
    if hashed == os.environ["ACCESS_KEY_HASH"]:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access key")

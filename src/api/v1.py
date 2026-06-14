"""Versioned JSON API (`/api/v1`).

All data endpoints live on `exercises_router`, which is guarded by
`check_access_key`. Auth endpoints live on `auth_router` and are intentionally
unauthenticated (you can't present a token before you have one).
"""
from datetime import date as date_cls, datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from starlette import status
from starlette.responses import JSONResponse

from src.dependencies import check_access_key, get_service
from src.dtos import (
    AddedDurationExerciseResponse,
    AddedRepsExerciseResponse,
    AddExerciseResponse,
    CreateExerciseInput,
    DurationExerciseStats,
    ExerciseHistoryEntry,
    ExercisesDaySumOutput,
    RepsExerciseStats,
    StatusResponse,
    TodaySummaryResponse,
)
from src.exercises_service import ExerciseService
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.fetching_exercises import sum_exercises

router = APIRouter(prefix="/api/v1")

exercises_router = APIRouter(dependencies=[Depends(check_access_key)])
auth_router = APIRouter(prefix="/auth")


@exercises_router.post("/exercises", response_model=AddExerciseResponse)
async def create_exercise(
        data: CreateExerciseInput,
        service: ExerciseService = Depends(get_service),
):
    """Create an exercise entry. The `type` field selects reps vs duration."""
    if data.type == "reps":
        result = service.add_reps_exercise(
            request=AddRepsExercisesRequest(name=data.name, reps=data.reps)
        )
        return AddExerciseResponse(data=AddedRepsExerciseResponse(**result))

    result = service.add_duration_exercise(
        request=AddDurationExercisesRequest(name=data.name, duration=data.duration)
    )
    return AddExerciseResponse(data=AddedDurationExerciseResponse(**result))


@exercises_router.get("/exercises", response_model=ExercisesDaySumOutput)
async def get_exercises(
        limit: int = Query(1000, ge=1, le=1000),
        offset: int = Query(0, ge=0, le=100000),
        last_days: int = Query(0, ge=0),
        service: ExerciseService = Depends(get_service),
):
    """Return exercises aggregated by day, with optional pagination and date filtering."""
    result = service.fetch_exercises(
        limit=limit, offset=offset, last_days=last_days or None
    )
    return sum_exercises(result)


@exercises_router.get("/exercises/{exercise_name}", response_model=list[ExerciseHistoryEntry])
async def get_exercise_history(
        exercise_name: str,
        limit: int = Query(1000, ge=1, le=1000),
        offset: int = Query(0, ge=0, le=100000),
        last_days: int = Query(0, ge=0),
        service: ExerciseService = Depends(get_service),
):
    """Return day-summed history for a specific exercise."""
    return service.get_exercise_history(
        name=exercise_name,
        limit=limit,
        offset=offset,
        last_days=last_days or None,
    )


@exercises_router.get(
    "/exercises/{exercise_name}/stats",
    response_model=RepsExerciseStats | DurationExerciseStats,
)
async def get_exercise_stats(
        exercise_name: str, service: ExerciseService = Depends(get_service)
):
    """Return aggregate statistics for a specific exercise."""
    result = service.get_exercise_stats(name=exercise_name)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise stats not found")
    return result


@exercises_router.get("/summary", response_model=TodaySummaryResponse)
async def get_summary(
        date: str = Query("today", description="ISO date (YYYY-MM-DD) or 'today'"),
        service: ExerciseService = Depends(get_service),
):
    """Return exercise totals grouped by name for a given day (defaults to today)."""
    if date == "today":
        day = datetime.now(pytz.timezone("Europe/Warsaw")).date()
    else:
        try:
            day = date_cls.fromisoformat(date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date; use ISO format (YYYY-MM-DD) or 'today'",
            )
    result = service.sum_exercises_for_day(day=day)
    return TodaySummaryResponse(exercises=result)


@auth_router.post("/token", response_model=StatusResponse)
async def set_auth_token(password: Annotated[str, Form()]):
    """Set the `access_token` cookie from a password form field."""
    response = JSONResponse(content=StatusResponse().model_dump())
    response.set_cookie(
        key="access_token",
        value=password,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


@auth_router.get("/session")
async def get_session(request: Request):
    """Return the current `access_token` cookie value (or null). Unauthenticated."""
    return {"access_token": request.cookies.get("access_token")}


router.include_router(exercises_router)
router.include_router(auth_router)

import os
from datetime import datetime
from typing import Annotated
from src.utils import get_hash
from dotenv import load_dotenv

import pytz
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from src.database_models import get_session
from src.dtos import (
    AddedDurationExerciseResponse,
    AddedRepsExerciseResponse,
    AddExerciseResponse,
    DurationExerciseInput,
    DurationExerciseStats,
    ExerciseHistoryEntry,
    ExercisesDaySumOutput,
    RepsExerciseInput,
    RepsExerciseStats,
    StatusResponse,
    TodaySummaryResponse,
)
from src.exercises_service import ExerciseService
from src.exercises_sources.dtos import (
    AddDurationExercisesRequest,
    AddRepsExercisesRequest,
)
from src.exercises_sources.sql import SQLExerciseSource
from src.fetching_exercises import sum_exercises
from src.get_table_data import get_table_data


def get_service() -> ExerciseService:
    exercises_source = SQLExerciseSource()
    return ExerciseService(exercise_source=exercises_source)


load_dotenv()


async def check_access_key(request: Request):
    access_key = request.headers.get("Authorization")
    if not access_key:
        access_key = request.cookies.get("access_token")
    hashed = get_hash(access_key)
    if hashed == os.environ["ACCESS_KEY_HASH"]:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access key")

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/table", response_class=HTMLResponse, dependencies=[Depends(check_access_key)])
async def get_table(
        request: Request,
        service: ExerciseService = Depends(get_service),
):
    """Render an HTML table of the latest exercises."""
    result = service.fetch_exercises(limit=10000)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        request,
        "exercise_table.html",
        {"exercise_names": exercise_names, "rows": rows},
    )


@app.post(
    "/reps",
    response_model=AddExerciseResponse,
    dependencies=[Depends(check_access_key)],
)
async def create_reps_exercise(
        data: RepsExerciseInput,
        service: ExerciseService = Depends(get_service),
):
    """Add a reps-based exercise entry."""
    request = AddRepsExercisesRequest(name=data.name, reps=data.reps)
    result = service.add_reps_exercise(request=request)
    return AddExerciseResponse(data=AddedRepsExerciseResponse(**result))


@app.post(
    "/duration",
    response_model=AddExerciseResponse,
    dependencies=[Depends(check_access_key)],
)
async def create_duration_exercise(
        data: DurationExerciseInput,
        service: ExerciseService = Depends(get_service),
):
    """Add a duration-based exercise entry."""
    request = AddDurationExercisesRequest(name=data.name, duration=data.duration)
    result = service.add_duration_exercise(request=request)
    return AddExerciseResponse(data=AddedDurationExerciseResponse(**result))


@app.get("/today", response_model=TodaySummaryResponse, dependencies=[Depends(check_access_key)])
async def get_today_summary(
        service: ExerciseService = Depends(get_service),
):
    """Return today's exercise totals grouped by exercise name."""
    cest = pytz.timezone("Europe/Warsaw")
    result = service.sum_exercises_for_day(day=datetime.now(cest).date())
    return TodaySummaryResponse(exercises=result)


@app.get("/exercises", response_model=ExercisesDaySumOutput, dependencies=[Depends(check_access_key)])
async def get_exercises(
        limit: int = Query(1000, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        last_days: int = Query(0, ge=0),
        service: ExerciseService = Depends(get_service),
):
    """Return exercises aggregated by day, with optional pagination and date filtering."""
    result = service.fetch_exercises(
        limit=limit, offset=offset, last_days=last_days or None
    )
    return sum_exercises(result)


@app.get("/exercises/{exercise_name}", response_model=list[ExerciseHistoryEntry],
         dependencies=[Depends(check_access_key)])
async def get_exercise_history(
        exercise_name: str,
        last_days: int = Query(0, ge=0),
        service: ExerciseService = Depends(get_service),
):
    """Return day-summed history for a specific exercise."""
    data = service.get_exercise_history(name=exercise_name, last_days=last_days or None)
    return data


@app.get("/")
async def get_auth_token(request: Request):
    """Return the current access token from cookies."""
    return request.cookies.get("access_token")


@app.get(
    "/exercises/{exercise_name}/stats",
    response_model=RepsExerciseStats | DurationExerciseStats,
    dependencies=[Depends(check_access_key)],
)
async def get_exercise_stats(
        exercise_name: str, service: ExerciseService = Depends(get_service)
):
    """Return aggregate statistics for a specific exercise."""
    result = service.get_exercise_stats(name=exercise_name)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise stats not found")
    return result


@app.post("/api/set_auth_token/", response_model=StatusResponse)
async def set_auth_token(password: Annotated[str, Form()]):
    from starlette.responses import JSONResponse

    response = JSONResponse(content=StatusResponse().model_dump())
    response.set_cookie(
        key="access_token",
        value=password,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


@app.get("/login", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse(request, "login.html")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

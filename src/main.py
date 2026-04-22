import os
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from src.database_models import get_session
from src.dtos import (
    AddExerciseResponse,
    AddedDurationExerciseResponse,
    AddedRepsExerciseResponse,
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


def get_service():
    exercises_source = SQLExerciseSource()
    return ExerciseService(exercise_source=exercises_source)


app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/table", response_class=HTMLResponse)
async def read_root(
    request: Request,
    service: ExerciseService = Depends(get_service),
):
    """Render an HTML table of the latest exercises."""
    result = service.fetch_exercises(limit=10000)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        "exercise_table.html",
        {"request": request, "exercise_names": exercise_names, "rows": rows},
    )


async def check_access_key(request: Request):
    access_key = request.headers.get("Authorization")
    if access_key == "my_strong_password":
        return True
    raise HTTPException(status_code=401, detail="Invalid access key")


@app.post("/reps", response_model=AddExerciseResponse, dependencies=[Depends(check_access_key)])
async def add_reps_exercise_post(
    data: RepsExerciseInput,
    service: ExerciseService = Depends(get_service),
):
    """Add a reps-based exercise entry."""
    request = AddRepsExercisesRequest(name=data.name, reps=data.reps)
    result = service.add_reps_exercise(request=request)
    return AddExerciseResponse(data=AddedRepsExerciseResponse(**result))


@app.post("/duration", response_model=AddExerciseResponse, dependencies=[Depends(check_access_key)])
async def add_duration_exercise_post(
    data: DurationExerciseInput,
    service: ExerciseService = Depends(get_service),
):
    """Add a duration-based exercise entry."""
    request = AddDurationExercisesRequest(name=data.name, duration=data.duration)
    result = service.add_duration_exercise(request=request)
    return AddExerciseResponse(data=AddedDurationExerciseResponse(**result))


@app.get("/today", response_model=TodaySummaryResponse)
async def read_today_json(
    service: ExerciseService = Depends(get_service),
):
    """Return today's exercise totals grouped by exercise name."""
    cest = pytz.timezone("Europe/Warsaw")
    result = service.sum_exercises_for_day(day=datetime.now(cest).date())
    return TodaySummaryResponse(exercises=result)


@app.get("/exercises", response_model=ExercisesDaySumOutput)
async def read_json(
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


@app.get("/exercises/{exercise_name}", response_model=list[ExerciseHistoryEntry])
async def get_exercise_history(
    exercise_name: str,
    last_days: int = Query(0, ge=0),
    service: ExerciseService = Depends(get_service),
):
    """Return day-summed history for a specific exercise."""
    data = service.get_exercise_history(name=exercise_name, last_days=last_days or None)
    return data


@app.get("/")
async def root(request: Request):
    """Return the current access token from cookies."""
    return request.cookies.get("access_token")


@app.get(
    "/exercises/{exercise_name}/stats",
    response_model=RepsExerciseStats | DurationExerciseStats,
)
async def get_exercise_stats_view(
    exercise_name: str, service: ExerciseService = Depends(get_service)
):
    """Return aggregate statistics for a specific exercise."""
    return service.get_exercise_stats(name=exercise_name)


@app.post("/api/set_auth_token/", response_model=StatusResponse)
async def set_auth_token_view(password: Annotated[str, Form()]):
    """Set an authentication token cookie."""
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
async def login_form():
    """Render a simple login form."""
    return """
    <form action="/api/set_auth_token/" method="post">
        <label>Password: <input type="password" name="password"></label>
        <button type="submit">Submit</button>
    </form>
    """


def test_exercise_endpoint():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/exercises")
    assert response.status_code == 200
    assert "exercises" in response.json()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

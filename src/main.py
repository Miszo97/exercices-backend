import os
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.database_models import get_session
from src.dtos import DurationExerciseInput, RepsExerciseInput
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
    result = service.fetch_exercises(limit=10000)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        "exercise_table.html",
        {"request": request, "exercise_names": exercise_names, "rows": rows},
    )


@app.post("/reps")
async def add_reps_exercise_post(
    data: RepsExerciseInput, service: ExerciseService = Depends(get_service)
):
    request = AddRepsExercisesRequest(name=data.name, reps=data.reps)
    result = service.add_reps_exercise(request=request)
    return {"status": "ok", "data": result}


@app.post("/duration")
async def add_duration_exercise_post(
    data: DurationExerciseInput, service: ExerciseService = Depends(get_service)
):
    request = AddDurationExercisesRequest(name=data.name, duration=data.duration)
    result = service.add_duration_exercise(request=request)
    return {"status": "ok", "data": result}


@app.get("/today")
async def read_today_json(
    service: ExerciseService = Depends(get_service),
):
    cest = pytz.timezone("Europe/Warsaw")
    result = service.fetch_exercises(day=datetime.now(cest))
    result = sum_exercises(result)
    return JSONResponse(content=result.model_dump()["exercises"])


@app.get("/exercises")
async def read_json(
    limit: int = Query(1000, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    last_days: int = Query(0, ge=0),
    service: ExerciseService = Depends(get_service),
):
    result = service.fetch_exercises(
        limit=limit, offset=offset, last_days=last_days or None
    )
    result = sum_exercises(result)
    return JSONResponse(content=result.model_dump())


@app.get("/exercises/{exercise_name}")
async def get_exercise_history(
    exercise_name: str,
    last_days: int = Query(0, ge=0),
    service: ExerciseService = Depends(get_service),
):
    # Delegate to service method that encapsulates the filtering and summing logic
    data = service.get_exercise_history(name=exercise_name, last_days=last_days or None)
    return JSONResponse(content=data)


@app.get("/exercises/{exercise_name}/stats")
async def get_exercise_stats_view(
    exercise_name: str, service: ExerciseService = Depends(get_service)
):
    stats = service.get_exercise_stats(name=exercise_name)
    return JSONResponse(content=stats.model_dump())


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

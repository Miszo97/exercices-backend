import os
from datetime import datetime

import firebase_admin
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import firestore
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.exercises_service import ExerciseService
from src.fetching_exercises import fetch_exercises, sum_exercises
from src.dtos import (
    ExerciseType,
    RepsExerciseDaySum,
    DurationExerciseDaySum,
    RepsExerciseInput,
    DurationExerciseInput,
)
from src.get_table_data import get_table_data

firebase_admin.initialize_app()
db = firestore.client()
service = ExerciseService(db)

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    result = fetch_exercises(db)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        "exercise_table.html",
        {"request": request, "exercise_names": exercise_names, "rows": rows},
    )


@app.post("/reps")
async def add_reps_exercise_post(data: RepsExerciseInput):
    result = service.add_reps_exercise(name=data.name, reps=data.reps)
    return {"status": "ok", "data": result}


@app.post("/duration")
async def add_duration_exercise_post(data: DurationExerciseInput):
    result = service.add_duration_exercise(
        name=data.name, duration=data.duration, unit=data.unit
    )
    return {"status": "ok", "data": result}


@app.get("/today")
async def read_today_json():
    result = fetch_exercises(db, day=datetime.now())
    result = sum_exercises(result)
    exercises_dict = []
    for ex in result:
        payload = {"name": ex.name}

        if isinstance(ex, RepsExerciseDaySum):
            payload["type"] = ExerciseType.REPS.value
            if getattr(ex, "reps", None):
                payload["reps"] = ex.reps
        elif isinstance(ex, DurationExerciseDaySum):
            payload["type"] = ExerciseType.DURATION.value
            if getattr(ex, "duration", None):
                payload["duration"] = ex.duration
        else:
            payload["type"] = None
            reps_val = getattr(ex, "reps", None)
            duration_val = getattr(ex, "duration", None)
            if reps_val:
                payload["reps"] = reps_val
            if duration_val:
                payload["duration"] = duration_val

        exercises_dict.append(payload)
    return JSONResponse(content=exercises_dict)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

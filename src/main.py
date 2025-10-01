import os
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.dtos import DurationExerciseInput, RepsExerciseInput
from src.exercises_service import ExerciseService
from src.fetching_exercises import sum_exercises
from src.get_table_data import get_table_data

service = ExerciseService()

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
    result = service.fetch_exercises()
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
    result = service.fetch_exercises(day=datetime.now())
    result = sum_exercises(result)
    return JSONResponse(content=result.model_dump())


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

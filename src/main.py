import os
from datetime import datetime
from typing import Optional

import firebase_admin
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import firestore
from pydantic import BaseModel
from starlette.responses import JSONResponse

from src.adding_exercise import add_exercise
from src.fetching_exercises import fetch_exercises, sum_exercises
from src.get_table_data import get_table_data

firebase_admin.initialize_app()
db = firestore.client()

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    result = fetch_exercises(db)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        "exercise_table.html",
        {"request": request, "exercise_names": exercise_names, "rows": rows},
    )


class ExerciseInput(BaseModel):
    name: str
    reps: Optional[int] = None
    duration: Optional[int] = None
    unit: Optional[str] = None


@app.post("/", response_class=HTMLResponse)
async def add_exercise_post(data: ExerciseInput):
    result = add_exercise(
        name=data.name, reps=data.reps, duration=data.duration, unit=data.unit, db=db
    )
    response_body = f"<html><body><h1>Exercise Added</h1><p>{result}</p></body></html>"
    return HTMLResponse(content=response_body, status_code=200)


@app.get("/today")
async def read_today_json():
    result = fetch_exercises(db, day=datetime.now())
    result = sum_exercises(result)
    exercises_dict = [{"name": ex.name, "reps": ex.reps, "duration": ex.duration} for ex in result]
    return JSONResponse(content=exercises_dict)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

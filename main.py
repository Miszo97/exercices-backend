import os
from typing import Optional

import firebase_admin
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from firebase_admin import credentials, firestore

from adding_exercise import add_exercise
from fetching_exercises import fetch_exercises
from get_table_data import get_table_data

firebase_admin.initialize_app()
db = firebase_admin.firestore.client()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    result = fetch_exercises(db)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        "exercise_table.html",
        {"request": request, "exercise_names": exercise_names, "rows": rows}
    )

@app.post("/", response_class=HTMLResponse)
async def add_exercise_post(
    request: Request,
    name: str = Form(...),
    reps: Optional[int] = Form(None),
    duration: Optional[int] = Form(None),
    unit: Optional[str] = Form(None)
):
    if not name:
        return JSONResponse(content={"error": "'name' field is required"}, status_code=status.HTTP_400_BAD_REQUEST)
    result = add_exercise(name=name, reps=reps, duration=duration, unit=unit, db=db)
    response_body = f"<html><body><h1>Exercise Added</h1><p>{result}</p></body></html>"
    return HTMLResponse(content=response_body, status_code=200)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from src.api.v1 import router as api_v1_router

# Re-exported so existing tests can do `from src.main import get_service, check_access_key`
# and so `app.dependency_overrides[...]` keys match the functions used by the routers.
from src.dependencies import check_access_key, get_service  # noqa: F401
from src.exercises_service import ExerciseService
from src.get_table_data import get_table_data

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JSON API — everything under /api/v1
app.include_router(api_v1_router)


@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/login", response_class=HTMLResponse)
async def get_login_form(request: Request):
    """Server-rendered login form."""
    return templates.TemplateResponse(request, "login.html")


@app.get("/table", response_class=HTMLResponse, dependencies=[Depends(check_access_key)])
async def get_table(
        request: Request,
        service: ExerciseService = Depends(get_service),
):
    """Server-rendered HTML table of all exercises (up to 10,000 entries)."""
    result = service.fetch_exercises(limit=10000)
    exercise_names, rows = get_table_data(exercises=result)
    return templates.TemplateResponse(
        request,
        "exercise_table.html",
        {"exercise_names": exercise_names, "rows": rows},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

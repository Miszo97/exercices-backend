# exercises-backend

## Commands

| Action | Command |
|--------|---------|
| Install deps | `uv sync` |
| Run dev server | `uv run uvicorn src.main:app --reload` (port 8080) |
| Run all tests | `uv run pytest` |
| Run single test | `uv run pytest src/tests/test_views.py -k test_name` |
| Run SQL source tests | `uv run pytest src/exercises_sources/sql/tests.py` |
| Docker (prod) | `docker compose up --build` |
| Docker (dev) | `docker compose -f docker-compose-dev.yml up --build` |
| Alembic (in Docker) | `docker compose exec app alembic upgrade head` |

## Architecture

- **FastAPI** app at `src/main.py` — entrypoint: `src.main:app`
- **Two exercise types**: reps (integer) and duration (seconds), stored in separate DB tables (`reps_exercise_entry`, `duration_exercise_entry`)
- **Layers**: `ExerciseSource` protocol → `SQLExerciseSource` impl → `ExerciseService` → FastAPI routes
- **DB**: SQLite in-memory by default (via `DB_URI` default `sqlite:///:memory:`), PostgreSQL in Docker/production
- **Auth**: SHA-256 hashed access key from `Authorization` header or `access_token` cookie, checked against `ACCESS_KEY_HASH` env var
- **Timezone**: Europe/Warsaw (`pytz`) for all timestamps
- **CORS**: allows `localhost:5173`, `localhost:8081`

## Testing quirks

- `conftest.py` creates/drops all tables per test via `session` fixture
- Two test styles coexist: **mocked** (`test_views.py` mocks `ExerciseService`) and **integration** (`test_views_integration.py`, `sql/tests.py` use real SQLite via `session` fixture)
- Integration tests override `check_access_key` dependency to bypass auth
- SQLite uses `StaticPool` so the same in-memory DB persists across the app — essential for integration tests
- Import style is inconsistent: some test files use `from src.xxx` (absolute), others `from xxx` (relative, relies on CWD)

## Key source layout

| File | Role |
|------|------|
| `src/main.py` | FastAPI app, routes, auth |
| `src/database_models.py` | SQLAlchemy models, engine/session factory |
| `src/dtos.py` | Shared Pydantic models + dataclass DTOs |
| `src/exercises_sources/exercises_source.py` | `ExerciseSource` protocol |
| `src/exercises_sources/sql/sql_exercises_source.py` | SQLAlchemy implementation |
| `src/exercises_service.py` | Service layer |
| `src/fetching_exercises.py` | Exercise summing logic |
| `src/get_table_data.py` | HTML table data prep |
| `src/utils.py` | Time formatting utility |
| `src/templates/` | Jinja2 templates (login + exercise table) |
| `migrations/` | Alembic migrations (DB_URI env var) |
| `.github/workflows/docker-image.yaml.yml` | CI: builds+pushes to GHCR on master push/PR |

## Gotchas

- `src/` is **not** an installed package — imports use `from src.xxx import yyy`
- `add_duration_exercise` / `add_reps_exercise` return plain `dict`s, not model instances
- `fetch_exercises` sorts **ascending** by date; `fetch_exercises_by_name` sorts **descending**
- `sum_exercises` uses `TypeGuard` / `TypeAlias` (Python 3.14 features)
- `pyrightconfig.json` sets `pythonVersion: "3.12"` but project requires `>=3.14` — pyright may miss some features
- Duplicate/misnamed CI file: `docker-image.yaml.yml` (used), `docker-image.yml` (stale reference)
- No ruff/mypy config in `pyproject.toml` — no automated linting/formatting

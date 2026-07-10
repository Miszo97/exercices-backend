# exercises-backend

FastAPI backend for tracking reps-based and duration-based exercise entries.

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
| Alembic (in Docker) | `docker compose exec app uv run alembic upgrade head` |

## Architecture

- **FastAPI** app at `src/main.py` — entrypoint `src.main:app`
- **Two exercise types** (reps / duration) stored in separate DB tables: `reps_exercise_entry`, `duration_exercise_entry`
- **Layers**: `ExerciseSource` protocol → `SQLExerciseSource` → `ExerciseService` → routes
- **DB**: SQLite in-memory by default (`DB_URI=sqlite:///:memory:`), PostgreSQL in Docker/production
- **Auth**: SHA-256 hashed key from `Authorization` header or `access_token` cookie, checked against `ACCESS_KEY_HASH` env var
- **Timezone**: Europe/Warsaw (`pytz`)
- **CORS**: `localhost:5173`, `localhost:8081`

## Testing

- `conftest.py` at `src/conftest.py` creates/drops all tables per test via `session` fixture
- Two styles coexist: **mocked** (`test_views.py` mocks `ExerciseService`) and **integration** (`test_views_integration.py`, `sql/tests.py` use real SQLite via `session` fixture)
- Integration tests override `check_access_key` dependency to bypass auth
- SQLite uses `StaticPool` so the same in-memory DB persists across the app — essential for integration tests
- Import style is inconsistent: some files use `from src.xxx` (absolute), others `from xxx` (relative, relies on CWD being project root)
- `src/tests/test_main.py` posts to `/set-auth-token` (non-existent) — that test is broken

## Key layout

| File | Role |
|------|------|
| `src/main.py` | FastAPI app, routes, auth dependency |
| `src/database_models.py` | SQLAlchemy models + engine/session factory |
| `src/dtos.py` | Pydantic models + dataclass DTOs |
| `src/exercises_sources/exercises_source.py` | `ExerciseSource` protocol |
| `src/exercises_sources/sql/sql_exercises_source.py` | SQLAlchemy impl |
| `src/exercises_service.py` | Service layer |
| `src/fetching_exercises.py` | Day-sum aggregation logic |
| `src/get_table_data.py` | HTML table data prep |
| `src/utils.py` | SHA-256 hash + time formatting |
| `src/templates/` | Jinja2 templates |
| `migrations/` | Alembic migrations (reads `DB_URI` env) |
| `migrations/versions/` | Migration scripts |

## Gotchas

- Docker Desktop must be running before using any `docker compose` commands locally

- `src/` is **not** an installed package — imports must use `from src.xxx import yyy`
- `add_duration_exercise` / `add_reps_exercise` return plain `dict`s, not model instances
- `fetch_exercises` sorts **ascending** by date; `fetch_exercises_by_name` sorts **descending**
- `sum_exercises` uses `TypeGuard` / `TypeAlias` (Python 3.14 features)
- `pyrightconfig.json` sets `pythonVersion: "3.12"` — pyright may report false errors for 3.14-only syntax
- No ruff/mypy config — no automated linting or formatting enforced
- Without Docker, in-memory SQLite via `Base.metadata.create_all()` — no migration needed locally
- Three compose files: `docker-compose.yml` (prod, port 8080, PG on 5432), `docker-compose-dev.yml` (dev, port 8090, PG on 5433), `docker-compose.local.yml` (local, port 8070, PG on 5434)
- `DEVELOPER.md` has deeper docs (API reference, deploy steps, env vars) — read it for full context

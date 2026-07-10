# Developer Guide — exercises-backend

A FastAPI backend for tracking reps-based and duration-based exercise entries, with PostgreSQL in production and SQLite in local/test environments.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Architecture](#architecture)
4. [Configuration & Environment Variables](#configuration--environment-variables)
5. [API Reference](#api-reference)
6. [Authentication](#authentication)
7. [Database & Migrations](#database--migrations)
8. [Testing](#testing)
9. [CI/CD & Deployment](#cicd--deployment)
10. [Known Gotchas](#known-gotchas)

---

## Quick Start

**Prerequisites:** Python 3.14+, [`uv`](https://github.com/astral-sh/uv)

```bash
# Install dependencies
uv sync

# Set required env var (any string, hashed with SHA-256)
export ACCESS_KEY_HASH=$(echo -n "mysecret" | sha256sum | awk '{print $1}')

# Run dev server (hot-reload, default port 8000)
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest
```

With Docker (PostgreSQL included):

```bash
docker compose up --build
# Apply migrations after first start
docker compose exec app uv run alembic upgrade head
```

---

## Project Structure

```
exercises-backend/
├── src/
│   ├── main.py                          # FastAPI app, all routes, auth dependency
│   ├── database_models.py               # SQLAlchemy ORM models + engine/session factories
│   ├── dtos.py                          # Shared Pydantic models and dataclass DTOs
│   ├── exercises_service.py             # Service layer (orchestrates ExerciseSource)
│   ├── fetching_exercises.py            # sum_exercises() — aggregates entries by day
│   ├── get_table_data.py                # Prepares data for HTML table rendering
│   ├── utils.py                         # SHA-256 hashing, time formatting
│   ├── exercises_sources/
│   │   ├── exercises_source.py          # ExerciseSource protocol (interface)
│   │   ├── dtos.py                      # Request DTOs for the source layer
│   │   └── sql/
│   │       ├── sql_exercises_source.py  # SQLAlchemy implementation
│   │       └── tests.py                 # Unit tests for SQLExerciseSource
│   ├── templates/
│   │   ├── login.html
│   │   ├── exercise_table.html
│   │   └── index.html
│   ├── tests/
│   │   ├── conftest.py                  # Pytest fixtures (DB session setup/teardown)
│   │   ├── test_views.py                # Mocked endpoint tests
│   │   ├── test_views_integration.py    # Integration tests (real SQLite)
│   │   ├── test_sum_exercises.py        # Unit tests for aggregation logic
│   │   ├── test_utils.py
│   │   └── test_main.py
├── migrations/
│   ├── versions/
│   │   └── 66d71a324368_create_a_baseline_migrations.py
│   └── env.py
├── Dockerfile
├── docker-compose.yml                   # Production (PostgreSQL)
├── docker-compose-dev.yml               # Dev/staging (PostgreSQL, separate DB)
├── docker-compose.local.yml             # Local development variant
├── compose.env                          # Env vars for production compose
├── compose.dev.env                      # Env vars for dev compose
├── alembic.ini
├── pyproject.toml
└── .github/workflows/docker-image.yaml.yml
```

---

## Architecture

The codebase is organized in explicit layers, top-to-bottom:

```
FastAPI routes (src/main.py)
       ↓
ExerciseService (src/exercises_service.py)
       ↓
ExerciseSource protocol (src/exercises_sources/exercises_source.py)
       ↓
SQLExerciseSource (src/exercises_sources/sql/sql_exercises_source.py)
       ↓
SQLAlchemy ORM + PostgreSQL / SQLite
```

### Key design points

- **Protocol-based data layer.** `ExerciseSource` is a `typing.Protocol`. The only production implementation is `SQLExerciseSource`. Tests inject a mock or the real source through FastAPI's `Depends`.
- **Two exercise types.** Reps (integer count) and duration (integer seconds) are stored in separate tables (`reps_exercise_entry`, `duration_exercise_entry`) and have separate DTOs, but share the same service interface.
- **Timezone.** All "today" logic uses `Europe/Warsaw` via `pytz`. Raw entries stored in the DB have UTC-equivalent datetimes; the timezone conversion happens at query time in the routes.
- **No session in routes.** Routes depend on `ExerciseService` (via `Depends(get_service)`), which internally manages DB sessions through `SQLExerciseSource`. Session lifecycle is handled inside the source layer.
- **CORS.** Configured to allow `http://localhost:5173` and `http://localhost:8081` for frontend development.

---

## Configuration & Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ACCESS_KEY_HASH` | Yes (prod) | — | SHA-256 hex digest of the access key |
| `DB_URI` | No | `sqlite:///:memory:` | SQLAlchemy database URL |
| `PORT` | No | `8080` | Port the server listens on |

`dotenv` is loaded at startup — place a `.env` file in the project root for local overrides.

**Generating `ACCESS_KEY_HASH`:**

```bash
echo -n "your-secret-key" | sha256sum | awk '{print $1}'
```

**Production DB URI (PostgreSQL):**

```
postgresql+psycopg://user:password@host:5432/dbname
```

The `compose.env` file ships a working default for Docker Compose:

```
DB_URI=postgresql+psycopg://postgres:postgres@db:5432/exercises
```

---

## API Reference

The JSON API lives under `/api/v1`. Server-rendered pages (`/login`, `/table`) and
`/health` live at the root. Everything under `/api/v1/exercises` and `/table`
requires authentication (see [Authentication](#authentication)); the `/api/v1/auth/*`
endpoints, `/login`, and `/health` do not.

### POST `/api/v1/exercises`

Create an exercise entry. The `type` field discriminates between reps- and
duration-based exercises (this replaces the old separate `/reps` and `/duration`
endpoints).

**Request body (reps):**
```json
{ "type": "reps", "name": "pushups", "reps": 20 }
```

**Request body (duration):**
```json
{ "type": "duration", "name": "plank", "duration": 60 }
```

**Response:**
```json
{
  "status": "ok",
  "data": { "id": 1, "date": "2025-10-26T10:00:00", "name": "pushups", "reps": 20, "type": "reps" }
}
```

---

### GET `/api/v1/summary`

Return totals grouped by exercise name for a given day.

**Query params:** `date` — an ISO date (`YYYY-MM-DD`) or `"today"` (default). `"today"` uses the Europe/Warsaw timezone.

**Response:**
```json
{ "exercises": { "pushups": 50, "plank": 120 } }
```

---

### GET `/api/v1/exercises`

Return all exercises aggregated by day (one entry per exercise per day).

**Query params:**

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 1000 | Max entries (1–1000) |
| `offset` | int | 0 | Skip N entries |
| `last_days` | int | 0 | Restrict to last N days (0 = no filter) |

**Response:**
```json
{
  "exercises": [
    { "date": "2025-10-26", "name": "pushups", "reps": 50, "duration": null },
    { "date": "2025-10-26", "name": "plank", "reps": null, "duration": 120 }
  ]
}
```

---

### GET `/api/v1/exercises/{exercise_name}`

Return day-summed history for a specific exercise, sorted descending by date.

**Query params:**

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 1000 | Max raw entries to read before day aggregation (1-1000) |
| `offset` | int | 0 | Skip N raw entries before day aggregation (0-100000) |
| `last_days` | int | 0 | Restrict to last N days (0 = no filter) |

**Response:**
```json
[
  { "date": "2025-10-26", "name": "pushups", "reps": 50, "duration": null }
]
```

---

### GET `/api/v1/exercises/{exercise_name}/stats`

Return aggregate stats for a specific exercise.

**Response (reps exercise):**
```json
{ "total_reps": 1200, "reps_in_last_30_days": 300 }
```

**Response (duration exercise):**
```json
{ "total_duration": 3600, "duration_in_last_30_days": 900 }
```

Returns `404` if the exercise name doesn't exist.

---

### GET `/table`

HTML response — renders an `exercise_table.html` Jinja2 template with all exercises (up to 10,000 entries).

---

### GET `/login`

HTML response — renders the `login.html` form.

---

### GET `/health`

Liveness probe. Returns `{ "status": "ok" }`. Unauthenticated.

---

### POST `/api/v1/auth/token`

Accepts a `password` form field. Sets an `access_token` cookie (httponly, secure, samesite=lax).

**Form body:** `password=your-secret-key`

**Response:** `{ "status": "ok" }`

---

### GET `/api/v1/auth/session`

Returns the current `access_token` cookie value (or `null`). Unauthenticated.

**Response:** `{ "access_token": "your-secret-key" }`

---

## Authentication

Every protected endpoint checks for an access key via `check_access_key` (a FastAPI `Depends`).
It is applied once at the router level for all `/api/v1/exercises*` routes, plus directly on `/table`:

1. Reads `Authorization` header, or falls back to `access_token` cookie.
2. SHA-256 hashes the value.
3. Compares against `ACCESS_KEY_HASH` env var.
4. Returns `401 Unauthorized` on mismatch.

The `/api/v1/auth/token` endpoint is the browser-friendly way to set the cookie. CLI usage:

```bash
curl -H "Authorization: your-secret-key" http://localhost:8080/api/v1/summary
```

---

## Database & Migrations

### ORM Models (`src/database_models.py`)

| Table | Model | Columns |
|---|---|---|
| `reps_exercise_entry` | `RepsExerciseEntry` | `id`, `date` (DateTime), `name` (String), `reps` (Integer) |
| `duration_exercise_entry` | `DurationExerciseEntry` | `id`, `date` (DateTime), `name` (String), `duration` (Integer) |

The engine is created once at import time from `DB_URI`. A `StaticPool` is used for SQLite (necessary for in-memory DBs to share state across threads in tests).

### Migrations (Alembic)

Alembic reads `DB_URI` from the environment. The baseline migration creates both tables.

```bash
# Apply all migrations
uv run alembic upgrade head

# Create a new migration (after changing ORM models)
uv run alembic revision --autogenerate -m "describe change"

# In Docker
docker compose exec app uv run alembic upgrade head
```

For local development against SQLite, the DB is in-memory by default — no migration is needed since `database_models.py` calls `Base.metadata.create_all()` on startup.

---

## Testing

```bash
# All tests
uv run pytest

# Specific file
uv run pytest src/tests/test_views.py

# Single test by name
uv run pytest src/tests/test_views.py -k test_get_today_summary

# SQL source unit tests
uv run pytest src/exercises_sources/sql/tests.py
```

### Two test styles

**Mocked** (`src/tests/test_views.py`):

- Uses `TestClient` with `app.dependency_overrides` to replace `get_service` with a `MagicMock`.
- Also overrides `check_access_key` to skip auth.
- Fast, no DB — good for testing route logic, response shapes, and auth behavior.

**Integration** (`src/tests/test_views_integration.py`, `src/exercises_sources/sql/tests.py`):

- Uses a real in-memory SQLite DB via the `session` fixture in `conftest.py`.
- The fixture creates all tables before the test and drops them after.
- Auth dependency is overridden to `lambda: True`.
- Tests the full stack including SQL queries.

### conftest.py fixture

```python
# Creates tables, runs test, drops tables — per test function
@pytest.fixture
def session():
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    Base.metadata.drop_all(engine)
```

**Why `StaticPool`:** SQLite in-memory databases are connection-scoped. `StaticPool` forces SQLAlchemy to reuse a single connection so the tables created by the fixture are visible to the app during the test.

---

## CI/CD & Deployment

### GitHub Actions (`.github/workflows/docker-deploy-image.yml`)

Triggers on push and PRs targeting `master` or `dev`.

| Step | When | What |
|---|---|---|
| Build Docker image | always | Builds with `docker/build-push-action` |
| Push to GHCR | push only (not PR) | Tags: branch name + `latest` (master only) |
| Deploy to VPS | push to master/dev | SSH into VPS, `docker compose pull && docker compose up -d` |

**Compose file selection on VPS:**
- `master` → `docker-compose.yml`
- `dev` → `docker-compose-dev.yml`

### Required GitHub secrets/vars

| Name | Type | Description |
|---|---|---|
| `VPS_SSH_KEY` | Secret | SSH private key for VPS access |
| `VPS_HOST` | Var | VPS hostname or IP |
| `VPS_USER` | Var | SSH username |
| `VPS_PORT` | Var | SSH port |
| `VPS_APP_DIR` | Var | Directory on VPS containing compose files |

### Docker image

Built from `python:3.14-alpine`. Uses `uv` for dependency installation. Exposes port `8080`.

```bash
# Build locally
docker build -t exercises-backend .

# Run with env file
docker run --env-file compose.env -p 8080:8080 exercises-backend
```

---

## Known Gotchas

- **`src/` is not an installed package.** Imports must use `from src.xxx import yyy`, not relative imports. Test files are inconsistent — some use `from src.xxx`, others use `from xxx` (relies on CWD being the project root).

- **`add_reps_exercise` / `add_duration_exercise` return plain `dict`s**, not model instances. Routes unpack them with `**result` into the response model constructors.

- **Sort order differs by endpoint.** `fetch_exercises` (used by `GET /api/v1/exercises`) sorts ascending by date. `fetch_exercises_by_name` (used by `GET /api/v1/exercises/{name}`) sorts descending.

- **`pyrightconfig.json` sets `pythonVersion: "3.12"`** even though the project requires `>=3.14`. Pyright may report false errors for 3.14-only features like `TypeGuard`/`TypeAlias` usage in `fetching_exercises.py`.

- **No ruff/mypy/black config** in `pyproject.toml`. There's no automated linting or formatting enforced in CI.

- **CI workflow filename is `docker-image.yaml.yml`** (double extension). There may be a stale `docker-image.yml` reference in some tooling — the active file is `docker-image.yaml.yml`.

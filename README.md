# Exercises Backend

A FastAPI-based backend service designed to track, manage, and analyze user exercise routines. It supports both repetition-based and duration-based exercises, offering historical data aggregation and statistical insights.

## Features

- **Exercise Tracking:** Add reps-based (e.g., pushups) and duration-based (e.g., planking) exercise entries.
- **Reporting & Analytics:**
  - View daily summaries grouped by exercise.
  - Fetch aggregated exercise history with pagination.
  - Get detailed statistics for specific exercises.
- **Security:** API endpoints are protected by an access key mechanism (validated via cookies or Authorization header).
- **Frontend:** Provides a basic HTML interface for logging in and viewing exercise data tables.

## Requirements

- Python `3.14+`
- `uv` (recommended) or `pip`

## Installation

```bash
uv sync
```

Or with `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running the Application

### Locally

```bash
uv run uvicorn src.main:app --reload
```

### Docker

To start with Docker Compose:

```bash
docker compose up --build
```
## Running Tests

```bash
uv run pytest
```

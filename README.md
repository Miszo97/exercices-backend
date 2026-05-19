### Exercises Backend

Backend service for working with exercises.

### Requirements

- Python `3.14+`
- `uv` (recommended) or `pip`

### Installation

```bash
uv sync
```

Or with `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run locally

```bash
uv run uvicorn src.main:app --reload
```

### Run tests

```bash
uv run pytest
```

### Docker

To start with Docker Compose:

```bash
docker compose up --build
```

For local development setup:

```bash
docker compose -f docker-compose-dev.yml up --build
```
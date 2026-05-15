FROM python:3.14-alpine

WORKDIR /app

RUN apk add --no-cache nodejs npm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN uv venv

COPY . .

RUN uv pip install .

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

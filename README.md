# BookClub Platform

A social reading platform with **private book clubs** at its core — readers keep a personal library (shelves, ratings, reviews, progress), and clubs read on a shared schedule with **spoiler-safe, milestone-gated discussions**. Positioned as a modern, privacy-first alternative to Goodreads, with first-class support for regional-language catalogs (e.g. Uzbek and Russian titles).

Full requirements: [docs/srs-bookclub-platform-v0.1.md](docs/srs-bookclub-platform-v0.1.md).

## Tech stack

- **API**: FastAPI (Python 3.11), SQLAlchemy 2.0 (async), Alembic migrations
- **Database**: PostgreSQL 16
- **Background jobs**: Celery, RabbitMQ (broker), Redis (result backend/cache), Flower (task monitoring)
- **Object storage**: MinIO (S3-compatible)
- **Observability**: Prometheus + Grafana (metrics), Loki + Promtail (logs)
- **Packaging**: Poetry
- **Deployment**: Docker Compose


## Getting started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ and [Poetry](https://python-poetry.org/) (for running the backend outside Docker)

### 1. Configure environment

Create a `.env` at the repo root (used by `docker-compose.yml`) and a `backend/.env` (used by the API/worker/beat containers).

### 2. Start the stack

```bash
docker compose up -d --build
```

This brings up Postgres, Redis, RabbitMQ, MinIO, the FastAPI app, Celery worker/beat, Flower, and the Prometheus/Grafana/Loki observability stack.

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### Services

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Flower (Celery monitoring) | http://localhost:5555 |
| MinIO console | http://localhost:9001 |
| RabbitMQ management | http://localhost:15672 |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |

### Running the backend locally (without Docker)

```bash
cd backend
poetry install
poetry run uvicorn src.backend.main:app --reload
```

Requires Postgres, Redis, and RabbitMQ reachable at the URLs configured in `backend/.env` (e.g. via `docker compose up postgres redis rabbitmq -d`).

### Running tests

```bash
cd backend
poetry run pytest
```

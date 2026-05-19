# Weather API

A small [FastAPI](https://fastapi.tiangolo.com/) service that returns current weather by city name using [Open-Meteo](https://open-meteo.com/) (geocoding + forecast). No API key is required.

## Stack

- Python 3.12 / FastAPI
- Package manager: [uv](https://docs.astral.sh/uv/)
- Formatter: black
- Linter: Ruff (lint only; formatting stays with black)
- Tests: pytest
- Containers: Docker / Docker Compose
- Database: MySQL (optional persistence via SQLAlchemy)
- CI: GitHub Actions

## Layout

```
.
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings / environment
│   ├── schemas.py        # Response models
│   ├── dependencies.py   # Dependency injection
│   ├── db.py             # SQLAlchemy engine and sessions
│   ├── models/           # ORM models
│   ├── repositories/   # Database access
│   ├── routers/          # HTTP routes
│   └── services/         # Business logic and external APIs
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── Makefile
```

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed

### Local development

```bash
make install

# Optional: pre-commit hooks
make pre-commit
```

## Run

### Docker Compose (recommended)

```bash
make run
```

The API listens on `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

The API container runs **uvicorn with `--reload`** and mounts `./app` into the container, so edits under `app/` are picked up automatically without rebuilding or restarting. Re-run `docker compose up --build` only when you change dependencies (`pyproject.toml` / `uv.lock`) or the `Dockerfile`.

This starts **MySQL** (`db`) and the **API** (`api`). Each successful `/weather` response is inserted into the `weather` table using the same fields as the JSON body (`city`, `temperature_celsius`, `description`, `humidity`, `wind_speed_mps`), plus `created_at`. Repeated requests on the same day create new rows. If MySQL is unavailable, the API still returns weather data (persistence is best-effort).

### Local (uv)

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
make test
```

Check formatting:

```bash
make lint
```

Format code:

```bash
make format
```

### Ruff (linting)

[Ruff](https://docs.astral.sh/ruff/) checks `app` and `tests` for common issues. It does not replace black; run both before opening a PR.

```bash
make ruff
```

## API example

### Request

```bash
curl "http://localhost:8000/weather?city=osaka"
```

### Sample response

```json
{
  "city": "osaka",
  "temperature_celsius": 22.5,
  "description": "clear sky",
  "humidity": 65,
  "wind_speed_mps": 3.2
}
```

### Error example

City not found (404):

```bash
curl -i "http://localhost:8000/weather?city=not-a-real-city-xyz"
```

### Weather history

Returns stored records from MySQL for a city (newest first). Requires a running database (`DATABASE_ENABLED=true`).

```bash
curl "http://localhost:8000/weather/history?city=osaka&limit=10"
```

Sample response:

```json
{
  "city": "osaka",
  "items": [
    {
      "id": 2,
      "city": "osaka",
      "temperature_celsius": 25.0,
      "description": "mainly clear",
      "humidity": 70,
      "wind_speed_mps": 4.0,
      "created_at": "2026-05-19T12:00:00+00:00"
    },
    {
      "id": 1,
      "city": "osaka",
      "temperature_celsius": 22.5,
      "description": "clear sky",
      "humidity": 65,
      "wind_speed_mps": 3.2,
      "created_at": "2026-05-19T11:00:00+00:00"
    }
  ]
}
```

### Login

Authenticate with email and password. Returns a JWT (valid for 7 days). Requires a user row in the `users` table (registration endpoint not implemented yet).

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"your-password"}'
```

Sample response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Environment variables

All are optional; defaults match the public Open-Meteo endpoints.

| Variable | Description |
|----------|-------------|
| `OPEN_METEO_GEOCODING_BASE_URL` | Base URL for the geocoding API |
| `OPEN_METEO_FORECAST_BASE_URL` | Base URL for the forecast API |
| `REQUEST_TIMEOUT_SECONDS` | HTTP client timeout (seconds) |
| `DATABASE_URL` | SQLAlchemy URL (default: local MySQL) |
| `DATABASE_ENABLED` | Set to `false` to skip persistence (e.g. tests) |
| `SECRET_KEY` | JWT signing secret (set a strong value in production) |

### MySQL (Docker Compose defaults)

| Setting | Value |
|---------|-------|
| Host | `db` (from API container) / `localhost` (from host) |
| Port | `3306` |
| Database | `weather` |
| User / password | `weather` / `weather` |
| Root password | `rootpassword` |

## Makefile targets

| Target | Description |
|--------|-------------|
| `make run` | Start the stack with Docker Compose |
| `make test` | Run pytest |
| `make lint` | Run black in check mode |
| `make format` | Format with black |
| `make ruff` | Run Ruff linter |
| `make install` | Install dependencies (including dev) |
| `make pre-commit` | Install pre-commit hooks |

## Example incremental commits

```bash
git init
git add pyproject.toml uv.lock .gitignore .env.example
git commit -m "chore: initialize project with uv"

git add app/
git commit -m "feat: add weather API endpoint"

git add tests/ .github/
git commit -m "test: add pytest and GitHub Actions"

git add Dockerfile docker-compose.yml Makefile README.md .pre-commit-config.yaml
git commit -m "chore: add Docker, Makefile, and documentation"
```

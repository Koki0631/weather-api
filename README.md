# Weather API

A small [FastAPI](https://fastapi.tiangolo.com/) service that returns current weather by city name using [Open-Meteo](https://open-meteo.com/) (geocoding + forecast). No API key is required.

## Stack

- Python 3.12 / FastAPI
- Package manager: [uv](https://docs.astral.sh/uv/)
- Formatter: black
- Tests: pytest
- Containers: Docker / Docker Compose
- CI: GitHub Actions

## Layout

```
.
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings / environment
│   ├── schemas.py        # Response models
│   ├── dependencies.py   # Dependency injection
│   ├── routers/          # HTTP routes
│   └── services/         # External API clients
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

## Environment variables

All are optional; defaults match the public Open-Meteo endpoints.

| Variable | Description |
|----------|-------------|
| `OPEN_METEO_GEOCODING_BASE_URL` | Base URL for the geocoding API |
| `OPEN_METEO_FORECAST_BASE_URL` | Base URL for the forecast API |
| `REQUEST_TIMEOUT_SECONDS` | HTTP client timeout (seconds) |

## Makefile targets

| Target | Description |
|--------|-------------|
| `make run` | Start the stack with Docker Compose |
| `make test` | Run pytest |
| `make lint` | Run black in check mode |
| `make format` | Format with black |
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

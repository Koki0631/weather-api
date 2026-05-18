.PHONY: run test lint format ruff install pre-commit

run:
	docker compose up --build

test:
	uv run pytest -v

lint:
	uv run black --check app tests

format:
	uv run black app tests

ruff:
	uv run ruff check app tests

install:
	uv sync --group dev

pre-commit:
	uv run pre-commit install

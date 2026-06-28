.PHONY: run test lint format

run:
	cd app && PYTHONPATH=.. uv run uvicorn app.main:create_application --factory --reload

test:
	cd app && uv run pytest tests -v

lint:
	cd app && uv run ruff check .

format:
	cd app && uv run ruff format .

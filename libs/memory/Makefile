.PHONY: setup install dev lint format type-check test ci clean

setup:
	uv sync --all-extras

install:
	uv sync

dev:
	uv sync --all-extras && uv run pytest -v

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

type-check:
	uv run pyrefly check

test:
	uv run pytest -v

test-cov:
	uv run pytest -v --cov --cov-report=html

ci: lint type-check test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete
	rm -rf .ruff_cache .pyrefly_cache *.egg-info dist build

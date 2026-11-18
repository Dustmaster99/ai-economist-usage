.PHONY: install run test lint format clean

install:
	uv sync --dev

run:
	uv run python main.py

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	uv run python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for name in ('__pycache__', '.pytest_cache', '.ruff_cache') for p in Path('.').rglob(name)]"

.PHONY: test lint fmt check build clean

test:
	python3 -m pytest

lint:
	python3 -m ruff check .
	python3 -m ruff format --check .

fmt:
	python3 -m ruff check --fix .
	python3 -m ruff format .

check: lint test

build:
	python3 -m build

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

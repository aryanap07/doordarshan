.PHONY: \
	help install dev run serve shell \
	test test-unit test-api test-ws coverage format lint typecheck check \
	revision migrate downgrade reset-db \
	build publish freeze clean

PYTHON := python
PIP := $(PYTHON) -m pip

APP := app.main:app
MODULE := app
SRC := app tests

help:
	@echo "Doordarshan development commands"
	@echo "  make install     Install runtime dependencies"
	@echo "  make dev         Install development dependencies"
	@echo "  make run         Run the development server"
	@echo "  make test        Run the complete test suite"
	@echo "  make test-unit   Run unit tests only"
	@echo "  make test-api    Run HTTP API tests only"
	@echo "  make test-ws     Run WebSocket tests only"
	@echo "  make coverage    Run tests and generate coverage reports"
	@echo "  make lint        Run Ruff checks"
	@echo "  make format      Format source and test files"
	@echo "  make typecheck   Run mypy"
	@echo "  make check       Run lint and tests without modifying files"
	@echo "  make migrate     Apply Alembic migrations"
	@echo "  make revision    Create an Alembic migration"
	@echo "  make build       Build wheel and source distributions"
	@echo "  make clean       Remove generated files"

install:
	$(PIP) install .

dev:
	$(PIP) install -e ".[dev]"

run:
	uvicorn $(APP) --reload

serve:
	uvicorn $(APP) --host 0.0.0.0 --port 8000

shell:
	$(PYTHON)

test:
	pytest -ra

test-unit:
	pytest -ra -m unit

test-api:
	pytest -ra -m api

test-ws:
	pytest -ra -m websocket

coverage:
	pytest -ra \
		--cov=$(MODULE) \
		--cov-report=term-missing:skip-covered \
		--cov-report=html \
		--cov-report=xml

lint:
	ruff check $(SRC)

format:
	black $(SRC)
	ruff check $(SRC) --fix

typecheck:
	mypy app

check: lint test

revision:
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

reset-db:
	alembic downgrade base
	alembic upgrade head

build:
	$(PYTHON) -m build

publish: build
	twine upload dist/*

freeze:
	$(PIP) freeze > requirements.txt

clean:
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name ".tox" -o -name ".nox" -o -name "htmlcov" \) -prune -exec rm -rf {} +
	find . -type f \( -name "*.py[co]" -o -name ".coverage*" \) -delete
	rm -rf build dist *.egg-info junit.xml coverage.xml

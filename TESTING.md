# Testing and CI

Doordarshan uses pytest for unit, HTTP API, and WebSocket tests. The test suite
creates a fresh in-memory SQLite database per test. It does not connect to a
developer database or a production database. The WebSocket endpoint's direct
SQLAlchemy session factory is redirected to the same isolated test database.

## Install

```bash
python -m pip install -e ".[dev]"
```

The project requires Python 3.11 or newer.

## Run tests

```bash
# Complete suite
pytest -ra

# By test layer
pytest -m unit -ra
pytest -m api -ra
pytest -m websocket -ra

# Coverage in the terminal, HTML, and XML formats
make coverage
```

The HTML coverage report is written to `htmlcov/index.html`. The XML report is
written to `coverage.xml` for CI/reporting integrations. No minimum coverage
threshold is enforced yet; establish a baseline from the first successful CI
runs before introducing a threshold that could conceal untested modules.

## Code quality

```bash
make lint       # Ruff
make format     # Black formatting and Ruff auto-fixes
make typecheck  # mypy
make check      # Ruff plus tests; does not rewrite files
```

## GitHub Actions

`.github/workflows/ci.yml` runs Ruff, the test matrix on Python 3.11/3.12/3.13,
a PostgreSQL migration smoke test, and a package build. Test reports are
uploaded as workflow artifacts.

`.github/workflows/security.yml` runs `pip-audit` on pull requests, pushes to
main/master, and weekly. This is intentionally a blocking security check: it
will report known vulnerabilities in the resolved dependency environment. In
particular, the current `python-jose==3.5.0` pin is the subject of the open
Dependabot security alert and must not be treated as remediated just because
the JWT decoder restricts its accepted algorithm. Resolve the dependency alert
through a verified patched release or a tested migration before expecting the
security workflow to pass.

`.github/workflows/codeql.yml` performs CodeQL advanced analysis for the
Python backend and JavaScript frontend. Before using this workflow, switch the
repository's CodeQL setting from **Default setup** to **Advanced setup** (the
committed workflow is the advanced configuration). Do not run the default and
advanced CodeQL setups simultaneously. The language matrix is explicit so
both `python` and `javascript-typescript` are analyzed.

`.github/dependabot.yml` also keeps GitHub Actions references up to date, in
addition to Python packages.

## Database test strategy

Fast API and WebSocket tests use SQLite to remain fast and isolated. CI also
starts PostgreSQL 16 and applies the repository's Alembic migrations to check
the supported production database path. The migration smoke test does not
replace integration testing against a separately managed staging database.

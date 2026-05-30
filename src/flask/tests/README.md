# Tests

## Running Tests

### Happy + Unhappy Path Tests

All routes are tested in `test_routes.py`. Each endpoint has at least one happy path test and one unhappy path test.

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test
python -m pytest tests/test_routes.py::test_login_success -v

# Run with verbose output
python -m pytest tests/ -v --tb=short
```

## Code Coverage

### Generate Coverage Report

```bash
# HTML report (open tests/htmlcov/index.html in browser)
python -m pytest tests/ --cov=backend --cov-report=html

# Terminal report
python -m pytest tests/ --cov=backend --cov-report=term-missing

# JSON report
python -m pytest tests/ --cov=backend --cov-report=json

# LCOV format
python -m pytest tests/ --cov=backend --cov-report=lcov

# XML (for CI/CD)
python -m pytest tests/ --cov=backend --cov-report=xml
```

### Coverage Configuration

Set in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=backend --cov-report=term-missing --cov-fail-under=60"
```

### Coverage Thresholds

To disable the coverage fail-under threshold:

```bash
python -m pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=0
```

### Quick Check

```bash
# Coverage summary only
python -m pytest tests/ --cov=backend --cov-report=term-missing --no-header -q
```

### Coverage Report Files

| Report Type | Command | Output |
|-------------|---------|--------|
| HTML | `--cov-report=html` | `tests/htmlcov/index.html` |
| Terminal | `--cov-report=term-missing` | stdout (in terminal) |
| JSON | `--cov-report=json` | stdout (JSON string) |
| LCOV | `--cov-report=lcov` | stdout (LCOV format) |
| XML | `--cov-report=xml` | `coverage.xml` |

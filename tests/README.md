# Tests

This directory contains the test suite for the LoFi IA YouTube application.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=api --cov-report=html
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Smoke tests
pytest -m smoke
```

### Run specific test files
```bash
pytest tests/test_api.py
pytest tests/test_models.py
pytest tests/test_schemas.py
```

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_api.py` - API endpoint tests
- `test_models.py` - SQLAlchemy ORM model tests
- `test_schemas.py` - Pydantic schema validation tests

## Test Markers

Tests are marked with the following categories:

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.integration` - Tests requiring database/Redis
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.smoke` - Basic smoke tests

## Coverage Reports

After running tests with coverage, view the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Writing Tests

### Example test structure

```python
import pytest

@pytest.mark.unit
def test_example(client):
    """Test description."""
    response = client.get("/endpoint")
    assert response.status_code == 200
```

### Using fixtures

```python
def test_with_sample_data(sample_event_data):
    """Use pre-defined test data."""
    assert sample_event_data["kind"] == "test_event"
```

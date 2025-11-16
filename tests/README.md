# Tests

This directory contains the test suite for the Flask application.

## Running Tests

### Using mise (recommended)

```bash
# Install mise if not already installed
curl https://mise.run | sh

# Install Python version (will be done automatically)
mise install

# Run all tests
pytest

# Run tests in parallel (faster - uses all CPU cores)
pytest -n auto

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run only unit tests (skip integration tests)
pytest -m "unit"

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m "integration"
```

### Without mise

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_config.py` - Configuration management tests
- `test_database.py` - Database utility tests
- `test_auth.py` - Authentication route tests
- `test_main.py` - Main application route tests
- `test_contact.py` - Contact form tests
- `test_utils.py` - Utility function tests

## Test Coverage

The test suite aims to cover:
- All route endpoints
- Authentication and authorization
- Input validation
- Error handling
- Security features (HTML escaping, etc.)

## Test Markers

Tests can be organized using markers:
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may require external services)
- `@pytest.mark.slow` - Slow tests (can be skipped during development)

Example:
```python
@pytest.mark.unit
def test_simple_function():
    assert 1 + 1 == 2

@pytest.mark.integration
def test_database_connection():
    # Test that requires database
    pass
```

## Parallel Testing

The project uses `pytest-xdist` for parallel test execution:
- `pytest -n auto` - Automatically uses all available CPU cores
- `pytest -n 4` - Use 4 worker processes
- Parallel execution significantly speeds up test runs on multi-core systems


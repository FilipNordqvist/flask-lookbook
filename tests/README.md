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

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
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


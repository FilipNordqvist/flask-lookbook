# Code Quality & Standards

This document describes the code quality tools and standards used in this project to ensure the code meets requirements for hosting platforms like Railway, Azure, Cloudflare, and others.

## Tools Used

### 1. **Ruff** - Linting & Formatting
- **Purpose**: Fast Python linter and formatter (replaces flake8, black, isort)
- **What it checks**: Code style, import organization, common errors, complexity
- **Configuration**: `ruff.toml` and `pyproject.toml`

### 2. **MyPy** - Type Checking
- **Purpose**: Static type checking to catch type errors before runtime
- **What it checks**: Type annotations, type consistency, potential type errors
- **Configuration**: `mypy.ini`

### 3. **Bandit** - Security Linting
- **Purpose**: Scans Python code for common security vulnerabilities
- **What it checks**: SQL injection, shell injection, hardcoded passwords, etc.
- **Configuration**: `.bandit`

### 4. **Safety** - Dependency Vulnerability Scanning
- **Purpose**: Checks dependencies for known security vulnerabilities
- **What it checks**: CVE database for vulnerable package versions
- **Configuration**: Uses `requirements.txt`

### 5. **Pytest** - Testing
- **Purpose**: Unit and integration testing
- **What it checks**: Code functionality, edge cases, error handling
- **Configuration**: `pytest.ini`

## Running Checks

### Quick Commands

```bash
# Install all tools
make install-dev

# Run all checks
make all

# Run individual checks
make lint          # Linting only
make format        # Format code
make type-check    # Type checking only
make security      # Security scan only
make test          # Tests only
```

### Using Makefile

The `Makefile` provides convenient commands:

```bash
make help          # Show all available commands
make lint          # Run ruff linter
make format        # Format code with ruff
make format-check  # Check formatting (for CI)
make type-check    # Run mypy
make security      # Run bandit
make safety        # Check dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make check         # Run all checks
make all           # Format, lint, type-check, security, and test
make clean         # Remove cache files
```

### Manual Commands

```bash
# Linting
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix issues
ruff format .                   # Format code
ruff format --check .           # Check formatting

# Type checking
mypy . --config-file mypy.ini

# Security
bandit -r . -c .bandit          # Security scan
safety check                     # Dependency vulnerabilities

# Testing
pytest                           # Run tests
pytest --cov=. --cov-report=html # With coverage
```

### Using the Check Script

```bash
# Run comprehensive checks
./scripts/check.sh
```

## Pre-commit Hooks

Install pre-commit hooks to automatically run checks before each commit:

```bash
pip install pre-commit
pre-commit install
```

This will run all checks automatically when you commit, preventing bad code from being committed.

## CI/CD Integration

For hosting platforms, add these checks to your CI/CD pipeline:

### Railway / Render / Fly.io
```yaml
# Example .railway.yml or similar
build:
  commands:
    - pip install -r requirements.txt
    - make format-check
    - make lint
    - make type-check
    - make security
    - make test
```

### GitHub Actions
```yaml
# .github/workflows/quality.yml
name: Code Quality
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: make all
```

## Code Standards

### Line Length
- Maximum line length: 100 characters
- This is a common standard that works well with modern displays

### Import Organization
- Imports are automatically sorted by ruff
- Order: standard library, third-party, local imports
- Each group separated by a blank line

### Type Hints
- Type hints are encouraged but not strictly required
- MyPy is configured to be lenient for gradual adoption

### Security Standards
- No hardcoded secrets (use environment variables)
- No SQL injection vulnerabilities (use parameterized queries)
- No shell injection (avoid shell=True in subprocess)
- Dependencies must not have known CVEs

### Testing Standards
- All routes should have tests
- Critical business logic should have tests
- Aim for >80% code coverage

## Common Issues & Fixes

### Ruff Issues
- **E501 (Line too long)**: Break long lines or use ruff format
- **F401 (Unused import)**: Remove unused imports
- **I001 (Import sorting)**: Run `ruff check --fix .` to auto-sort

### MyPy Issues
- **Missing type stubs**: Add `# type: ignore` for third-party packages
- **Untyped function**: Add type hints gradually

### Bandit Issues
- **B101 (assert_used)**: OK in tests, add to ignore list
- **B601 (shell_injection)**: Use subprocess with list args, not shell=True

## Platform-Specific Requirements

### Railway
- Code must pass all linting checks
- Tests must pass
- No security vulnerabilities in dependencies

### Azure
- Follows Python best practices
- Type checking recommended
- Security scanning required

### Cloudflare Workers (if using Python)
- Code quality standards apply
- Fast startup time (avoid heavy imports)

### Heroku / Render
- Standard Python practices
- Clean code without warnings

## Continuous Improvement

- Run `make all` before committing
- Fix issues as they arise
- Gradually add type hints
- Keep dependencies updated
- Review security reports regularly


# Makefile for running code quality checks
# This makes it easy to run all linting, formatting, and testing commands

.PHONY: help lint format type-check security test test-cov clean install install-dev check all

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install all dependencies including dev tools"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with ruff"
	@echo "  make format-check  - Check if code is formatted (CI mode)"
	@echo "  make type-check    - Run mypy type checker"
	@echo "  make security      - Run bandit security scanner"
	@echo "  make safety        - Check dependencies for vulnerabilities"
	@echo "  make test          - Run pytest tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make check         - Run all checks (lint, type, security, test)"
	@echo "  make all           - Format, lint, type-check, security, and test"
	@echo "  make clean         - Remove cache files and build artifacts"

# Installation
install:
	pip install -r requirements.txt

install-dev: install
	pip install ruff mypy bandit safety

# Linting
lint:
	@echo "Running ruff linter..."
	ruff check .

lint-fix:
	@echo "Running ruff linter with auto-fix..."
	ruff check --fix .

# Formatting
format:
	@echo "Formatting code with ruff..."
	ruff format .

format-check:
	@echo "Checking code formatting..."
	ruff format --check .

# Type checking
type-check:
	@echo "Running mypy type checker..."
	mypy . --config-file mypy.ini

# Security checks
security:
	@echo "Running bandit security scanner..."
	bandit -r . -c .bandit -f json -o bandit-report.json || true
	bandit -r . -c .bandit

safety:
	@echo "Checking dependencies for vulnerabilities..."
	safety check --json || true
	safety check

# Testing
test:
	@echo "Running pytest tests..."
	pytest

test-cov:
	@echo "Running pytest with coverage..."
	pytest --cov=. --cov-report=term-missing --cov-report=html

# Run all checks
check: lint type-check security test
	@echo "All checks completed!"

# Format, lint, type-check, security, and test
all: format lint-fix type-check security test
	@echo "All quality checks passed!"

# Cleanup
clean:
	@echo "Cleaning cache files and build artifacts..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "bandit-report.json" -delete 2>/dev/null || true
	@echo "Cleanup complete!"


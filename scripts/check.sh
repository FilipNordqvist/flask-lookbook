#!/bin/bash
# Comprehensive code quality check script
# This script runs all linting, type checking, security, and testing tools
# Exit on any error
set -e

echo "🔍 Running comprehensive code quality checks..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run a check and report status
run_check() {
    local name=$1
    local command=$2
    
    echo -e "${YELLOW}Running ${name}...${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ ${name} passed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ ${name} failed${NC}"
        echo ""
        return 1
    fi
}

# Track failures
FAILED=0

# 1. Format check
run_check "Code Formatting" "ruff format --check ." || FAILED=$((FAILED + 1))

# 2. Linting
run_check "Linting" "ruff check ." || FAILED=$((FAILED + 1))

# 3. Type checking
run_check "Type Checking" "mypy . --config-file mypy.ini" || FAILED=$((FAILED + 1))

# 4. Security scanning
run_check "Security Scan" "bandit -r . -c .bandit -q" || FAILED=$((FAILED + 1))

# 5. Dependency vulnerability check
run_check "Dependency Safety" "safety check --short-report" || FAILED=$((FAILED + 1))

# 6. Tests
run_check "Tests" "pytest --tb=short" || FAILED=$((FAILED + 1))

# Summary
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ ${FAILED} check(s) failed${NC}"
    exit 1
fi


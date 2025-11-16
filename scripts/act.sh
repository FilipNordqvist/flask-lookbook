#!/bin/bash
# Script to run act in a Docker container safely
# Usage: ./scripts/act.sh [act arguments]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting act in Docker container...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if container exists, create if not
if ! docker ps -a --format '{{.Names}}' | grep -q "^flask-lookbook-act$"; then
    echo -e "${GREEN}Creating act container...${NC}"
    docker-compose -f docker-compose.act.yml up -d
    # Wait a moment for container to be ready
    sleep 2
fi

# Start container if not running
if ! docker ps --format '{{.Names}}' | grep -q "^flask-lookbook-act$"; then
    echo -e "${GREEN}Starting act container...${NC}"
    docker-compose -f docker-compose.act.yml start
fi

# Run act with all passed arguments
echo -e "${BLUE}Running: act $@${NC}"
# Install act if not already installed, then run it
# Use -i instead of -it when TTY is not available (e.g., in scripts)
if [ -t 0 ]; then
    docker exec -it flask-lookbook-act bash -c "command -v act >/dev/null 2>&1 || (curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | bash) && export PATH=\$PATH:/root/.local/bin:\$(pwd)/bin && act \"\$@\"" -- "$@"
else
    docker exec -i flask-lookbook-act bash -c "command -v act >/dev/null 2>&1 || (curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | bash) && export PATH=\$PATH:/root/.local/bin:\$(pwd)/bin && act \"\$@\"" -- "$@"
fi


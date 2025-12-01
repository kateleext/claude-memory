#!/bin/bash
# Setup script for Claude Memory MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "Error: Python 3.10+ required. You have Python $PYTHON_VERSION."
    echo ""
    echo "Options:"
    echo "  - macOS: brew install python@3.12"
    echo "  - Ubuntu: sudo apt install python3.12"
    echo "  - Or use pyenv: pyenv install 3.12"
    exit 1
fi

echo "Using Python $PYTHON_VERSION"

# Create venv
echo "Creating virtual environment..."
python3 -m venv venv

# Upgrade pip and install
echo "Installing dependencies..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install -r requirements.txt --quiet

echo ""
echo "Done! Now run:"
echo "  claude mcp add memory \"$SCRIPT_DIR/run.sh\""
echo ""
echo "Then restart Claude Code."

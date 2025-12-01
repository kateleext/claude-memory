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
    echo "Error: Python 3.10+ required (you have $PYTHON_VERSION)."
    echo ""
    echo "The MCP SDK requires Python 3.10+. Help the user upgrade Python using"
    echo "pyenv, homebrew, or their system package manager, then re-run ./setup.sh"
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

echo "Registering with Claude Code (user level)..."
claude mcp add memory -s user "$SCRIPT_DIR/run.sh"

echo ""
echo "Done! Restart Claude Code to load the memory server."

#!/bin/bash
# MCP Server wrapper script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if present (for custom paths)
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

exec "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/server.py"
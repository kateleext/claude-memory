"""
Claude Memory MCP Server

Gives Claude Code persistent memory across sessions by indexing conversation history.
"""

import os

# Configuration
CLAUDE_PROJECTS_PATH = os.environ.get(
    "CLAUDE_PROJECTS_PATH",
    os.path.expanduser("~/.claude/projects")
)

NOTES_PATH = os.environ.get(
    "CLAUDE_MEMORY_NOTES_PATH",
    os.path.expanduser("~/.claude/memory-notes.json")
)

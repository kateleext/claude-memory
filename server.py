#!/usr/bin/env python3
"""
Claude Memory MCP Server

Gives Claude Code persistent memory across sessions by indexing conversation history.
Uses todos as chapter markers, activity signals for context, and manual notes for breadcrumbs.
"""

from memory.tools import mcp

if __name__ == "__main__":
    mcp.run()

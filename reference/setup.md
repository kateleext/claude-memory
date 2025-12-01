# Setup Guide

## Quick Start

```bash
# Clone the repo
git clone https://github.com/kateleext/claude-memory.git
cd claude-memory

# Create Python environment
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Add to Claude Code
claude mcp add memory "$(pwd)/run.sh"
```

Restart Claude Code. The memory tools are now available.

## Verify Installation

In a Claude Code session, ask:

> "What projects do you have access to in memory?"

Claude should use `list_projects()` and return your project folders.

## Configuration

The server reads conversations from `~/.claude/projects/` by default.

To customize:

```bash
# Create .env file in the repo
echo 'CLAUDE_PROJECTS_PATH=/your/custom/path' > .env
echo 'CLAUDE_MEMORY_NOTES_PATH=/your/custom/notes.json' >> .env
```

## Troubleshooting

**"No sessions found"**
- Check that `~/.claude/projects/` exists and contains `.jsonl` files
- Ensure you've had at least one Claude Code conversation

**"Tool not found"**
- Restart Claude Code after adding the MCP server
- Verify run.sh is executable: `chmod +x run.sh`

**Permission errors**
- The server needs read access to `~/.claude/projects/`
- Notes are written to `~/.claude/memory-notes.json`

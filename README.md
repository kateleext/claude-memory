# Memory Palace

An MCP server that gives Claude Code persistent memory across sessions.

Built for my own use. I hope it helps you the way it's helped me. Feedback and PRs welcome.

## The Idea

5% till auto-compact. You ask for a quick summary before it's gone, but much of the detail is lost. Before you know it, your codebase root has 50 markdown files, each from a different Claude under pressure.

Sessions are arbitrary boundaries, and your entire conversation history already exists raw on disk. The problem is what gets loaded when. This server gives Claude a way to search and retrieve what it needs. Start fresh freely. Document with dedicated agents who can read the raw history with clean context.

## Quick Start

Ask Claude Code:

> Install the memory server from https://github.com/kateleext/claude-memory

Claude will read `INSTALLATION.md` and walk you through it. Requires Python 3.10+.

## Tools

| Tool | What it does |
|------|--------------|
| `search_memory` | Find sessions by keyword. Searches todos, notes, files touched, with full-text fallback. |
| `list_recent` | Browse recent sessions with summaries. |
| `list_chapters` | See session structure: chapters (from todos), pending work, notes. |
| `read_messages` | Load actual content by chapter, turn, or range. |
| `add_note` | Leave a breadcrumb on a session for future searches. |
| `list_projects` | See available project names for filtering. |

## How It Works

**Todos as chapters.** When you use TodoWrite, those todos become a structured index. Each completed todo marks a chapter boundary. The more diligently you use todos during sessions, the more navigable your memory becomes.

**Multiple signals.** Search checks todos (3x weight), notes (3x), files touched (2x), commands run (1x), and full text as fallback.

**Progressive depth.** Search first, get the outline, then pull just what you need. Avoid loading full conversations into context.

**Access, not synthesis.** This server provides raw access to your conversations. If you want synthesis, digests, or summaries, prompt a subagent to read your history and produce what you need. The synthesis layer is yours to define.

## Use Cases

- **Clean context**: conversation got bloated, start fresh and pull just the parts you need
- **Knowledge transfer**: document how a project came together to share with teammates
- **Decision archaeology**: find where and why a past decision was made
- **Resume abandoned work**: pick up where you left off weeks ago

See `reference/use-cases.md` for example prompts.

## Configuration

Reads from `~/.claude/projects/` by default. Notes stored at `~/.claude/memory-notes.json`.

To customize:

```bash
export CLAUDE_PROJECTS_PATH="/your/path/here"
export CLAUDE_MEMORY_NOTES_PATH="/your/path/notes.json"
```

## Troubleshooting

**"No sessions found"**: You need conversation history in `~/.claude/projects/`.

**Search returns nothing**: Try broader terms. The server stems words, so "authenticate" matches "authentication".

**Missing chapters**: Chapters come from completed todos. Sessions without TodoWrite usage will still be searchable, but won't have chapter structure.

## Privacy

- All data stays on your machine
- Read-only access to conversation files

## License

MIT

---

Questions or ideas? kate@takuma.ai or open an issue.

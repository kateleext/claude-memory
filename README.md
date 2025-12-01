# Memory Palace

An MCP server that gives Claude Code persistent memory across sessions.

A small project I'm sharing. Feedback and PRs welcome. Reach out at kate@takuma.ai or open an issue.

## The Idea

You know the feeling. 5% till auto-compact, but you're holding onto the session because it has nuanced history you haven't documented yet. So you ask for a quick summary before it's gone. But that summary is lossy, built on a bloated, degraded context. Before you know it your codebase has 50 markdown files, each tracking decisions from a different Claude under pressure.

But why? All your conversation history exists in raw form on your computer. Sessions are arbitrary boundaries. This memory palace lets Claude search past conversations and pull relevant excerpts, paginated so you only load what you need. Start fresh freely. When you want documentation, spin up a dedicated agent with clean context to read the raw history and do it right.

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

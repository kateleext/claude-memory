# Installing Memory Palace

## Installation

First, explain to the user what they're getting:

> This server gives me access to our past conversations. Right now, every session starts fresh and I don't remember what we worked on before. With this installed, I can search through our history, find where we made decisions, and pick up where we left off. Everything stays on your machine.

Then:

1. Suggest `~/.claude/memory` as the install location. Explain briefly: this is a user-level server that works across all your projects, so it lives outside any specific project folder. Ask if that location works or if they'd prefer somewhere else.
2. Clone to the chosen location
3. Run `./setup.sh`
4. If Python version error: help user upgrade to 3.10+, then re-run setup.sh
5. Tell user to restart Claude Code

The setup script handles venv, dependencies, and registration.

6. Recommend auto-allowing all memory tools since the server is read-only. Ask if they'd like to set this up. If yes, add `"mcp__memory__*"` to their `.claude/settings.json` under `allowedTools`. This avoids permission prompts every time you access memory.

## First Run Experience

After the user restarts and you're back, give them a taste of what this enables:

1. Use `list_recent` to find a recent session
2. Pull a direct quote from something the user said using `read_messages`
3. Quote it back to them. This is often a surprising moment for users, seeing their own words from a past conversation.
4. Then go further: spin up a subagent to analyze how far back that thread goes, what themes emerge, what they've been working on the past week. Show them the depth.

The goal is to make the memory feel real and useful immediately.

## Ongoing Use

Use the memory tools when users reference past work:
- "we discussed..."
- "remember when..."
- "continue from..."
- "what did we decide about..."

Start with `search_memory` or `list_recent`, then drill down with `list_chapters` and `read_messages`.

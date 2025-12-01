"""
MCP Tool definitions for the memory server.
"""

import os
import glob as glob_module
from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import CLAUDE_PROJECTS_PATH
from .stemmer import stem_query
from .extraction import parse_jsonl_file, extract_text_content
from .cache import get_cache, ensure_cache_fresh, parse_timestamp
from .notes import load_notes, get_notes_for_session, add_note_to_session


mcp = FastMCP("memory")


@mcp.tool()
async def list_recent(
    limit: int = 20,
    project: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None
) -> dict:
    """
    Browse recent sessions. Use when starting fresh or looking for recent work.

    Args:
        limit: Max sessions to return (default: 20)
        project: Filter by project name
        after: Only sessions after this date (ISO format, e.g., "2025-01-15")
        before: Only sessions before this date

    Returns:
        Sessions sorted by recency with summaries from todos or user messages
    """
    ensure_cache_fresh()
    load_notes()

    after_dt = parse_timestamp(after) if after else None
    before_dt = parse_timestamp(before) if before else None

    conversations = []
    cache = get_cache()

    for session_id, data in cache.items():
        if project and project not in data.get('project', ''):
            continue

        conv_dt = parse_timestamp(data.get('timestamp', ''))
        if after_dt and conv_dt and conv_dt < after_dt:
            continue
        if before_dt and conv_dt and conv_dt > before_dt:
            continue

        completed = data['final_todos'].get('completed', [])
        pending = data['final_todos'].get('pending', [])
        in_progress = data['final_todos'].get('in_progress', [])
        notes = get_notes_for_session(session_id)

        if completed:
            summary = ', '.join(completed[:3])
        else:
            arc = data.get('user_message_arc', [])
            user_turn_count = data.get('user_message_count', 0)

            if len(arc) == 1:
                summary = f"[1 turn] {arc[0]}"
            elif len(arc) == 2:
                summary = f"[{user_turn_count} turns] {arc[0]} ... {arc[1]}"
            else:
                summary = data.get('first_message', 'No todos')

        conversations.append({
            'sessionId': session_id,
            'project': data.get('project', ''),
            'timestamp': data.get('timestamp', ''),
            'summary': summary,
            'completed': completed,
            'inProgress': in_progress,
            'pending': pending,
            'messageCount': data.get('message_count', 0),
            'userMessageCount': data.get('user_message_count', 0),
            'hasChapters': len(data.get('chapters', [])) > 0,
            'filesTouched': data.get('files_touched', [])[:5],
            'hasNotes': len(notes) > 0
        })

    conversations.sort(key=lambda x: x['timestamp'] or '', reverse=True)
    return {'sessions': conversations[:limit]}


@mcp.tool()
async def search_memory(
    query: str,
    limit: int = 20,
    project: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    search_mode: str = "smart"
) -> dict:
    """
    Find past sessions by keyword. Searches todos, notes, files touched, and full text.

    Use when user references past work: "we discussed...", "remember when...", "continue from..."

    Args:
        query: Search terms (e.g., "oauth", "basecamp", "server.py")
        limit: Max results (default: 20)
        project: Filter by project name
        after: Only sessions after this date (ISO format)
        before: Only sessions before this date
        search_mode: "smart" (default), "todos", "full", or "files"

    Returns:
        Ranked sessions with match source and summaries
    """
    ensure_cache_fresh()
    load_notes()

    after_dt = parse_timestamp(after) if after else None
    before_dt = parse_timestamp(before) if before else None

    query_stems = stem_query(query)
    query_terms = query.lower().split()
    results = []
    cache = get_cache()

    for session_id, data in cache.items():
        if project and project not in data.get('project', ''):
            continue

        conv_dt = parse_timestamp(data.get('timestamp', ''))
        if after_dt and conv_dt and conv_dt < after_dt:
            continue
        if before_dt and conv_dt and conv_dt > before_dt:
            continue

        score = 0
        matched_todos = []
        matched_files = []
        matched_notes = []
        match_source = []

        all_todos = (data['final_todos'].get('completed', []) +
                    data['final_todos'].get('in_progress', []) +
                    data['final_todos'].get('pending', []))

        if search_mode in ['smart', 'todos']:
            for todo in all_todos:
                todo_lower = todo.lower()
                matches = sum(1 for term in query_terms if term in todo_lower)
                if matches > 0:
                    score += matches * 3
                    matched_todos.append(todo)
                    if 'todos' not in match_source:
                        match_source.append('todos')

            stemmed_todos = data.get('stemmed_todos', set())
            stem_matches = len(query_stems & stemmed_todos)
            if stem_matches > 0 and not matched_todos:
                score += stem_matches * 2
                if 'todos_stemmed' not in match_source:
                    match_source.append('todos_stemmed')

        notes = get_notes_for_session(session_id)
        for note in notes:
            note_lower = note.lower()
            matches = sum(1 for term in query_terms if term in note_lower)
            if matches > 0:
                score += matches * 3
                matched_notes.append(note)
                if 'notes' not in match_source:
                    match_source.append('notes')

        if search_mode in ['smart', 'files']:
            files = data.get('files_touched', [])
            for f in files:
                f_lower = f.lower()
                if any(term in f_lower for term in query_terms):
                    score += 2
                    matched_files.append(f)
                    if 'files' not in match_source:
                        match_source.append('files')

        if search_mode in ['smart', 'full']:
            commands = data.get('commands_run', [])
            for cmd in commands:
                cmd_lower = cmd.lower()
                if any(term in cmd_lower for term in query_terms):
                    score += 1
                    if 'commands' not in match_source:
                        match_source.append('commands')

        if search_mode in ['smart', 'full'] and score == 0:
            stemmed_terms = data.get('stemmed_terms', set())
            stem_matches = len(query_stems & stemmed_terms)
            if stem_matches > 0:
                score += stem_matches
                match_source.append('full_text')

            arc = data.get('user_message_arc', [])
            for msg in arc:
                msg_lower = msg.lower()
                if any(term in msg_lower for term in query_terms):
                    score += 1
                    if 'messages' not in match_source:
                        match_source.append('messages')

        if score > 0:
            completed = data['final_todos'].get('completed', [])

            if completed:
                summary = ', '.join(completed[:3])
            else:
                arc = data.get('user_message_arc', [])
                user_turn_count = data.get('user_message_count', 0)
                if len(arc) == 2:
                    summary = f"[{user_turn_count} turns] {arc[0][:80]} ... {arc[1][:80]}"
                elif len(arc) == 1:
                    summary = f"[{user_turn_count} turns] {arc[0][:100]}"
                else:
                    summary = data.get('first_message', '')[:100]

            results.append({
                'sessionId': session_id,
                'score': score,
                'matchSource': match_source,
                'matchedTodos': matched_todos[:5],
                'matchedFiles': matched_files[:5],
                'matchedNotes': matched_notes[:3],
                'summary': summary,
                'project': data.get('project', ''),
                'timestamp': data.get('timestamp', ''),
                'userMessageCount': data.get('user_message_count', 0),
                'hasChapters': len(data.get('chapters', [])) > 0
            })

    results.sort(key=lambda x: (x['score'], x['timestamp'] or ''), reverse=True)

    return {
        'results': results[:limit],
        'totalMatches': len(results),
        'searchMode': search_mode,
        'queryStems': list(query_stems)
    }


@mcp.tool()
async def add_note(session_id: str, note: str) -> dict:
    """
    Leave a breadcrumb on a session for future searches.

    Use when a session lacks todos but contains valuable decisions or insights.
    Notes are searchable via search_memory() and appear in list_chapters().

    Args:
        session_id: Session ID from search_memory() or list_recent()
        note: Concise, searchable note (1-2 sentences). Focus on decisions, not summaries.

    Returns:
        Confirmation with total notes on this session
    """
    total = add_note_to_session(session_id, note)

    return {
        'success': True,
        'sessionId': session_id,
        'note': note,
        'totalNotes': total
    }


@mcp.tool()
async def list_chapters(session_id: str) -> dict:
    """
    See the structure of a session: chapters (from completed todos), pending work, files touched, and notes.

    Args:
        session_id: Session ID from search_memory() or list_recent()

    Returns:
        Chapters with message ranges, pending work, activity signals, and any notes
    """
    ensure_cache_fresh()
    load_notes()

    cache = get_cache()

    if session_id not in cache:
        return {
            'error': f'Session "{session_id}" not found. Use search_memory() or list_recent() to find valid session IDs.',
            'success': False
        }

    data = cache[session_id]
    notes = get_notes_for_session(session_id)

    return {
        'success': True,
        'sessionId': session_id,
        'chapters': data.get('chapters', []),
        'pendingWork': [
            {'title': todo, 'status': 'pending'}
            for todo in data['final_todos'].get('pending', [])
        ] + [
            {'title': todo, 'status': 'in_progress'}
            for todo in data['final_todos'].get('in_progress', [])
        ],
        'notes': notes,
        'filesTouched': data.get('files_touched', []),
        'commandsRun': data.get('commands_run', [])[:10],
        'urlsFetched': data.get('urls_fetched', [])[:10],
        'totalMessages': data.get('message_count', 0),
        'userTurns': data.get('user_message_count', 0)
    }


@mcp.tool()
async def read_messages(
    session_id: str,
    chapter: Optional[int] = None,
    turn: Optional[int] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    expand: int = 0,
    include_assistant: bool = True
) -> dict:
    """
    Load actual message content from a session. Use after list_chapters to read specific parts.

    Navigation modes (first one wins):
    - chapter: Read messages from that chapter (1-indexed, from list_chapters)
    - turn: Read messages around that user turn (1-indexed)
    - start/end: Read raw message index range

    Args:
        session_id: Session ID from search_memory() or list_recent()
        chapter: Chapter number to read (1-indexed)
        turn: User turn to center on (1-indexed), with context
        start: Start message index (if not using chapter/turn)
        end: End message index (if not using chapter/turn)
        expand: Extra messages before/after (default: 0)
        include_assistant: Include assistant responses (default: True)

    Returns:
        Messages with navigation info for paging forward/backward
    """
    ensure_cache_fresh()

    cache = get_cache()

    if session_id not in cache:
        return {
            'error': f'Session "{session_id}" not found. Use search_memory() or list_recent() to find valid session IDs.',
            'success': False
        }

    data = cache[session_id]
    file_path = data.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return {
            'error': 'Session file not found on disk.',
            'success': False
        }

    entries = parse_jsonl_file(file_path)
    messages = []
    message_index = 0
    user_turn_count = 0

    for entry in entries:
        if entry.get('type') in ['user', 'assistant']:
            message_index += 1

            if entry.get('type') == 'user' and entry.get('message'):
                user_turn_count += 1
                messages.append({
                    'role': 'user',
                    'content': extract_text_content(entry['message'].get('content', '')),
                    'timestamp': entry.get('timestamp', ''),
                    'index': message_index,
                    'userTurn': user_turn_count
                })
            elif entry.get('type') == 'assistant' and entry.get('message'):
                text_parts = []
                for item in entry['message'].get('content', []):
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                messages.append({
                    'role': 'assistant',
                    'content': '\n'.join(text_parts),
                    'timestamp': entry.get('timestamp', ''),
                    'index': message_index,
                    'userTurn': user_turn_count
                })

    total_messages = len(messages)
    chapters = data.get('chapters', [])
    navigation_mode = None
    actual_start = 0
    actual_end = total_messages

    if chapter is not None:
        navigation_mode = 'chapter'
        if chapter < 1 or chapter > len(chapters):
            chapter_titles = [f"{i+1}: {c['title']}" for i, c in enumerate(chapters)]
            return {
                'error': f'Chapter {chapter} not found. This session has {len(chapters)} chapters: {chapter_titles}',
                'success': False
            }
        ch = chapters[chapter - 1]
        actual_start = ch['message_range'][0]
        actual_end = ch['message_range'][1]

    elif turn is not None:
        navigation_mode = 'turn'
        if turn < 1 or turn > user_turn_count:
            return {
                'error': f'Turn {turn} out of range. This session has {user_turn_count} user turns.',
                'success': False
            }
        context_turns = 2
        target_start_turn = max(1, turn - context_turns)
        target_end_turn = min(user_turn_count, turn + context_turns)

        selected = []
        for msg in messages:
            msg_turn = msg.get('userTurn', 0)
            if target_start_turn <= msg_turn <= target_end_turn:
                if include_assistant or msg['role'] == 'user':
                    selected.append(msg)

        return {
            'success': True,
            'sessionId': session_id,
            'navigationMode': 'turn',
            'requestedTurn': turn,
            'turnRange': (target_start_turn, target_end_turn),
            'totalUserTurns': user_turn_count,
            'messages': selected,
            'canPageBackward': target_start_turn > 1,
            'canPageForward': target_end_turn < user_turn_count
        }

    elif start is not None and end is not None:
        navigation_mode = 'range'
        actual_start = max(0, start)
        actual_end = min(total_messages, end)

    else:
        return {
            'error': 'Specify how to navigate: chapter=N, turn=N, or start/end range. Use list_chapters() first to see available chapters.',
            'success': False
        }

    actual_start = max(0, actual_start - expand)
    actual_end = min(total_messages, actual_end + expand)

    selected_messages = messages[actual_start:actual_end]

    if not include_assistant:
        selected_messages = [msg for msg in selected_messages if msg['role'] == 'user']

    return {
        'success': True,
        'sessionId': session_id,
        'navigationMode': navigation_mode,
        'messageRange': (actual_start, actual_end),
        'messages': selected_messages,
        'totalMessages': total_messages,
        'totalUserTurns': user_turn_count,
        'canExpandBefore': actual_start > 0,
        'canExpandAfter': actual_end < total_messages
    }


@mcp.tool()
async def list_projects() -> dict:
    """
    List available projects. Use to discover valid project names for filtering.

    Returns:
        List of project directory names (e.g., "-Users-kate-Projects-myapp")
    """
    project_dirs = [d for d in glob_module.glob(os.path.join(CLAUDE_PROJECTS_PATH, "*"))
                   if os.path.isdir(d)]
    projects = [os.path.basename(d) for d in project_dirs]

    return {'projects': projects}

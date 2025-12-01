"""
Notes storage - breadcrumbs left on sessions for future searches.
"""

import os
import json
from typing import Dict, List

from . import NOTES_PATH


# In-memory cache
_notes_cache: Dict[str, List[str]] = {}


def load_notes():
    """Load notes from disk"""
    global _notes_cache
    try:
        if os.path.exists(NOTES_PATH):
            with open(NOTES_PATH, 'r') as f:
                _notes_cache = json.load(f)
    except Exception as e:
        print(f"Error loading notes: {e}")
        _notes_cache = {}


def save_notes():
    """Save notes to disk"""
    try:
        with open(NOTES_PATH, 'w') as f:
            json.dump(_notes_cache, f, indent=2)
    except Exception as e:
        print(f"Error saving notes: {e}")


def get_notes_for_session(session_id: str) -> List[str]:
    """Get notes for a specific session"""
    return _notes_cache.get(session_id, [])


def add_note_to_session(session_id: str, note: str) -> int:
    """Add a note to a session, returns total notes count"""
    load_notes()

    if session_id not in _notes_cache:
        _notes_cache[session_id] = []

    _notes_cache[session_id].append(note)
    save_notes()

    return len(_notes_cache[session_id])

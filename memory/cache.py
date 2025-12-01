"""
In-memory cache management for conversation data.
"""

import os
import glob as glob_module
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from . import CLAUDE_PROJECTS_PATH
from .extraction import extract_conversation_data


# In-memory cache
_conversation_cache: Dict[str, Dict[str, Any]] = {}


def get_cache() -> Dict[str, Dict[str, Any]]:
    """Get the conversation cache"""
    return _conversation_cache


def ensure_cache_fresh():
    """
    Check file mtimes and re-parse only changed conversations.
    First run: ~5s to parse all files
    Subsequent: ~60ms (stat calls + search)
    """
    global _conversation_cache

    all_files = glob_module.glob(os.path.join(CLAUDE_PROJECTS_PATH, "*", "*.jsonl"))

    for file_path in all_files:
        try:
            current_mtime = os.path.getmtime(file_path)
            filename = os.path.basename(file_path)
            session_id = filename.replace('.jsonl', '')

            if (session_id not in _conversation_cache or
                _conversation_cache[session_id].get('mtime', 0) < current_mtime):

                data = extract_conversation_data(file_path)
                data['mtime'] = current_mtime
                data['file_path'] = file_path

                _conversation_cache[session_id] = data

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue


def parse_timestamp(ts: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime, normalized to UTC"""
    if not ts:
        return None
    try:
        ts = ts.replace('Z', '+00:00')
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except:
        return None

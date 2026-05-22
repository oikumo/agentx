"""Single source of truth for KB entry-ID generation.

Replaces the duplicated logic that previously lived in both
`rag_tool.rag_add_entry` and `rag_ingest._add_entry`.

ID scheme (unchanged from the pre-refactor implementation, so existing
ChromaDB rows remain compatible):

    {PREFIX}-{4-char-uppercase-md5-suffix}

where PREFIX is one of:

    pattern    -> PAT
    finding    -> FIND
    decision   -> DEC
    correction -> COR
    (other)    -> KB
"""

import hashlib
from datetime import datetime
from typing import Optional


_PREFIX_MAP = {
    "pattern": "PAT",
    "finding": "FIND",
    "decision": "DEC",
    "correction": "COR",
}


def make_entry_id(entry_type: str, category: str, title: str = "",
                  now: Optional[datetime] = None) -> str:
    """Build a unique KB entry ID.

    Args:
        entry_type: one of "pattern", "finding", "decision", "correction".
        category: the category string (used only for hash entropy).
        title: optional title (used only for hash entropy).
        now: optional datetime override, for tests.

    Returns:
        A string like "PAT-1A2B" or "FIND-7C9D".
    """
    if now is None:
        now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S%f")
    random_val = hash(f"{entry_type}{category}{title}{timestamp}") % 10000
    hash_input = f"{entry_type}{category}{timestamp}{random_val}"
    hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
    prefix = _PREFIX_MAP.get(entry_type, "KB")
    return f"{prefix}-{hash_val}"

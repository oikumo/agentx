from dataclasses import dataclass


@dataclass
class HistoryEntry:
    command: str
    id: int = 0
    created_at: str = ""

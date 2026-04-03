from dataclasses import dataclass


@dataclass
class HistoryEntry:
    id: int
    command: str
    created_at: str

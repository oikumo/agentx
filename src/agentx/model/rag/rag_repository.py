from dataclasses import dataclass


@dataclass
class RagRepository:
    path: str | None
    id: str | None
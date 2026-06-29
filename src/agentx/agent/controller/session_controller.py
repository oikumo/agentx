"""SessionController — snapshot save/load operations (operation_spec §2).

No SQL here — delegates to the Agent's persistence layer (MVC++).
"""

from __future__ import annotations

from agentx.agent.model.agent import Agent
from agentx.agent.types import SessionSnapshot


class SessionController:
    """Handles session persistence operations."""

    def __init__(self, agent: Agent) -> None:
        self._agent = agent

    def save_snapshot(self) -> str:
        """Persist the current Agent state as a SessionSnapshot (operation spec §2.1)."""
        return self._agent.persist()

    def load_snapshot(self, snapshot_id: str) -> SessionSnapshot | None:
        """Read a SessionSnapshot by id (operation spec §2.2)."""
        return self._agent._db.load_snapshot(snapshot_id)  # noqa: SLF001

    def resume_snapshot(self, snapshot_id: str) -> None:
        """Restore agent state from a snapshot."""
        self._agent.resume_session(snapshot_id)

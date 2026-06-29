"""Abstract Partners — MVC++ dependency-inversion contracts.

All Partners inherit from :class:`abc.ABC`.  Controllers depend on these
abstractions, never on concrete Model/View classes.  This keeps the View ↔ Model
isolation enforced by ``mvc_check.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.agent.types import (
        ActuatorCommand,
        ActuatorResult,
        AgentConfig,
        EnvironmentModel,
        EvictionCriteria,
        Goal,
        GoalTree,
        MemoryEntry,
        MemoryQuery,
        PolicyContext,
        PolicyDecision,
        PolicyRule,
        Proposal,
        ProposalVerdict,
        ReflectionEntry,
        RuleMetadata,
        SessionSnapshot,
    )


# ---------------------------------------------------------------------------
# Agent Model Partner — the controller's view of the Agent facade
# ---------------------------------------------------------------------------


class IAgentModelPartner(ABC):
    """Abstract Partner: Controller → Agent contract."""

    @abstractmethod
    def start_session(self, config: AgentConfig) -> str:
        """Initialize a new Agent and return its id."""

    @abstractmethod
    def resume_session(self, snapshot_id: str) -> None:
        """Rebuild the Agent from a persisted snapshot."""

    @abstractmethod
    def submit_goal(self, goal: Goal) -> str:
        """Add a goal to the goal tree and return its id."""

    @abstractmethod
    def run_cycle(self) -> Any:
        """Execute one perceive → decide → act → reflect cycle."""

    @abstractmethod
    def update_policy(self, rule: PolicyRule) -> bool:
        """Add or replace a policy rule via the safe path."""

    @abstractmethod
    def get_status(self) -> Any:
        """Return a serializable status snapshot."""

    @abstractmethod
    def persist(self) -> str:
        """Persist the current state and return the snapshot id."""


# ---------------------------------------------------------------------------
# View Partner — Controller → View contract
# ---------------------------------------------------------------------------


class IAgentViewPartner(ABC):
    """Abstract Partner: View → Controller contract (what the controller asks the view to show)."""

    @abstractmethod
    def show_status(self, status: Any) -> None:
        """Display agent status (state, autonomy, goals, etc.)."""

    @abstractmethod
    def show_reflection_log(self, entries: list[ReflectionEntry]) -> None:
        """Display reflection history."""

    @abstractmethod
    def show_memory_view(self, query: MemoryQuery) -> None:
        """Search/show memory entries."""

    @abstractmethod
    def show_policy_editor(self, rules: list[PolicyRule]) -> None:
        """Display policy rule editor."""

    @abstractmethod
    def refresh_goal_tree(self) -> None:
        """Redraw goal tree after changes."""

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Show a generic info message."""


# ---------------------------------------------------------------------------
# Subsystem Partners — Agent facade → subsystem contracts
# ---------------------------------------------------------------------------


class IMemoryStorePartner(ABC):
    """Abstract Partner for the memory subsystem."""

    @abstractmethod
    def store(self, entry: MemoryEntry, tier: Any) -> None: ...

    @abstractmethod
    def retrieve(self, query: MemoryQuery) -> list[MemoryEntry]: ...

    @abstractmethod
    def consolidate(self) -> int: ...

    @abstractmethod
    def evict(self, criteria: EvictionCriteria) -> int: ...


class IPolicyStorePartner(ABC):
    """Abstract Partner for the policy subsystem."""

    @abstractmethod
    def add_rule(self, rule: PolicyRule) -> None: ...

    @abstractmethod
    def remove_rule(self, rule_id: str) -> None: ...

    @abstractmethod
    def resolve_conflicts(self) -> dict[str, Any]: ...


class IGoalManager(ABC):
    """Abstract Partner for goal management (feature_001 swap point)."""

    @abstractmethod
    def add_goal(self, goal: Goal) -> str: ...

    @abstractmethod
    def get_goal(self, goal_id: str) -> Goal | None: ...

    @abstractmethod
    def get_tree(self) -> GoalTree: ...

    @abstractmethod
    def update_status(self, goal_id: str, status: Any) -> None: ...


class IToolRegistryPartner(ABC):
    """Abstract Partner for the tool registry."""

    @abstractmethod
    def list_sensors(self) -> list[str]: ...

    @abstractmethod
    def list_actuators(self) -> list[str]: ...

    @abstractmethod
    def get_spec(self, tool_id: str) -> Any:
        """Return the ToolSpec for *tool_id*."""

    @abstractmethod
    def health_check(self) -> dict[str, bool]: ...


class ISafetyEvaluator(ABC):
    """Abstract Partner for proposal safety evaluation (§8.4)."""

    @abstractmethod
    def evaluate(self, proposal: Proposal, ctx: PolicyContext) -> ProposalVerdict: ...


class IAIServicePartner(ABC):
    """Abstract Partner wrapping the existing :class:`AIService`.

    Keeps the agent subsystem decoupled from the concrete AI provider stack.
    """

    @abstractmethod
    def complete(self, prompt: str) -> str: ...


class IPersistencePartner(ABC):
    """Abstract Partner for session persistence."""

    @abstractmethod
    def save_snapshot(self, snapshot: SessionSnapshot) -> bool: ...

    @abstractmethod
    def load_snapshot(self, snapshot_id: str) -> SessionSnapshot: ...

"""Demo scenarios — seeded goal + policy rules + sandbox files (feature_010).

Pure data + a filesystem-seeding helper.  No UI imports, no controller imports.
The :class:`AgentController` consumes these specs via
:meth:`load_demo_scenario_by_name` (see ``agent_controller.py``).

Two scenarios are provided (selectable at runtime):

* ``SCENARIO_A`` — "File Reader Agent" (simple, one cycle): a single rule reads
  a seeded ``target.txt`` and the goal completes.
* ``SCENARIO_B`` — "Knowledge Assistant" (multi-step): a first rule reads
  ``notes.txt``, a second rule (firing on ``memory_contains("notes")``) queries
  the RAG knowledge base.  Showcases the condition DSL, memory, and multi-tool
  orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Lightweight spec dataclasses (translated to real Goal/PolicyRule by the
# controller, so this module stays decoupled from agent.types).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GoalSpec:
    """Serializable description of a demo goal."""

    description: str
    priority: int = 50
    success_kind: str = "tool_success"
    success_tool_id: str | None = None
    success_expression: str | None = None


@dataclass(frozen=True)
class RuleSpec:
    """Serializable description of a demo policy rule."""

    condition_expr: str
    action_type: str = "EXECUTE_TOOL"
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: int = 500


@dataclass(frozen=True)
class DemoScenario:
    """A complete demo recipe: one goal, N rules, and seed files."""

    key: str  # short lookup key, e.g. "a"
    name: str  # human-readable name
    description: str
    goal: GoalSpec
    rules: list[RuleSpec] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)  # relpath -> content


# ---------------------------------------------------------------------------
# Scenario A — File Reader Agent (simple, one cycle)
# ---------------------------------------------------------------------------

SCENARIO_A = DemoScenario(
    key="a",
    name="File Reader Agent",
    description="A single rule reads a seeded file and the goal completes in one cycle.",
    goal=GoalSpec(
        description="Read target.txt and report its contents",
        priority=80,
        success_kind="tool_success",
        success_tool_id="filesystem",
    ),
    rules=[
        RuleSpec(
            condition_expr="goal.active",
            action_type="EXECUTE_TOOL",
            parameters={
                "tool_id": "filesystem",
                "action": "read",
                "path": "target.txt",
            },
            priority=900,
        ),
    ],
    files={
        "target.txt": (
            "AgentX demo file.\n"
            "This content was read by the intelligent agent's filesystem tool.\n"
        ),
    },
)


# ---------------------------------------------------------------------------
# Scenario B — Knowledge Assistant (multi-step)
#
# A two-cycle flow that showcases the condition DSL (memory_contains, AND, NOT),
# memory-driven decisions, and multi-cycle orchestration — using only the
# built-in filesystem tool (no external RAG dependency):
#   cycle 1: goal.active → read notes.txt            (goal completes on success)
#   cycle 2: memory has "notes.txt" but not "summary.txt" → create summary.txt
#   cycle 3: summary.txt now exists → no rule fires (demo naturally idles)
# ---------------------------------------------------------------------------

SCENARIO_B = DemoScenario(
    key="b",
    name="Knowledge Assistant",
    description=(
        "A multi-step flow: cycle 1 reads seeded notes (goal completes); "
        "cycle 2 writes a summary report driven by the condition DSL "
        "(memory_contains + AND + NOT). Demonstrates memory-driven decisions "
        "and multi-cycle orchestration."
    ),
    goal=GoalSpec(
        description="Read the project notes and write a summary report",
        priority=80,
        success_kind="tool_success",
        success_tool_id="filesystem",
    ),
    rules=[
        RuleSpec(
            condition_expr="goal.active",
            action_type="EXECUTE_TOOL",
            parameters={
                "tool_id": "filesystem",
                "action": "read",
                "path": "notes.txt",
            },
            priority=900,
        ),
        RuleSpec(
            condition_expr='memory_contains("notes.txt") AND NOT memory_contains("summary.txt")',
            action_type="EXECUTE_TOOL",
            parameters={
                "tool_id": "filesystem",
                "action": "create",
                "path": "summary.txt",
                "content": "Summary: the agent read the notes and produced this report.",
            },
            priority=800,
        ),
    ],
    files={
        "notes.txt": (
            "Project Notes — Knowledge Assistant Demo\n"
            "=========================================\n"
            "1. The agent perceives its environment via sensors.\n"
            "2. The policy engine evaluates rules against the context.\n"
            "3. The selected action is executed by an actuator tool.\n"
            "4. Memory records the result for the next cycle.\n"
        ),
    },
)


# Ordered registry (key -> scenario).  Keys are matched case-insensitively.
SCENARIOS: dict[str, DemoScenario] = {
    s.key: s for s in (SCENARIO_A, SCENARIO_B)
}


def get_scenario(name: str) -> DemoScenario | None:
    """Look up a scenario by its short key (``"a"`` / ``"b"``), case-insensitive.

    Returns ``None`` when the key is unknown.
    """
    if not name:
        return None
    return SCENARIOS.get(name.strip().lower())


def list_scenarios() -> list[DemoScenario]:
    """Return all available scenarios in definition order."""
    return [SCENARIO_A, SCENARIO_B]


def seed_sandbox_files(scenario: DemoScenario, sandbox_root: str | Path) -> list[str]:
    """Write the scenario's seed files into *sandbox_root*.

    Overwrites existing files so a re-seed (reset) is idempotent.  Returns the
    list of relative paths written.  Parent directories are created as needed.
    """
    root = Path(sandbox_root)
    root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for relpath, content in scenario.files.items():
        target = (root / relpath).resolve()
        # Guard against path escape (defence in depth, mirrors FileSystemTool).
        if not str(target).startswith(str(root.resolve())):
            raise ValueError(f"scenario file escapes sandbox: {relpath}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(relpath)
    return written

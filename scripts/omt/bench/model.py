"""Task-cost benchmark data model (feature_093.task_cost_benchmark).

Pure data + validation: a TaskDef is a deterministic scripted agent session;
each Step either does work, verifies state, or deliberately violates a harness
rule. The probe executes the steps against the real enforcer; metrics.py then
accounts the transcript. No policy lives here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STEP_KINDS = {"omt", "edit", "write", "read", "search", "bash", "verify", "assert"}
ROLES = {"work", "intervention", "recovery", "verify", "violation"}
EXPECTS = {"ok", "blocked", "pass", "fail"}
MODES = {"real", "fixture"}
KNOWN_REMOVAL_GATES = {
    "g.nav",
    "g.protect",
    "g.receipt",
    "g.tests",
    "g.net",
    "g.phase",
    "g.think",
    "g.kb",
}


@dataclass(frozen=True)
class Step:
    """One deterministic agent action.

    kind:
      omt    — execute an omt_* tool (args = {tool, arguments})
      edit   — exact replace {path, old, new}
      write  — create/overwrite {path, content} or append {path, append}
      read   — bounded read {path, offset?, limit?}
      search — doc/code search {path?, pattern} (g.nav applies to doc scopes)
      bash   — opencode-core permission-checked shell command {command}
      verify — allowed shell command whose rc is evidence {command}
      assert — pure transcript assertion about another step {step, ...}

    expect: ok (allowed or success envelope), blocked (refused/blocked),
    pass (rc==0 / assertion true), fail (rc!=0 expected).
    role=violation marks seeded rule violations measured as TP/missed.
    gate= annotates a ceremony step as costing the named gate (removal model).
    tag= marks metric buckets (e.g. orientation).
    session= overrides the task default session (concurrent A/B).
    """

    id: str
    kind: str
    args: dict[str, Any] = field(default_factory=dict)
    role: str = "work"
    expect: str = "ok"
    session: str | None = None
    gate: str | None = None
    tag: str | None = None
    note: str = ""


@dataclass(frozen=True)
class TaskDef:
    id: str
    description: str
    mode: str = "real"
    setup: str | None = None
    session: str = ""
    steps: tuple[Step, ...] = ()
    seeded_faults: tuple[str, ...] = ()
    manifest: dict[str, Any] = field(default_factory=dict)

    def to_spec(self) -> dict[str, Any]:
        """JSON-serializable probe spec payload."""
        return {
            "id": self.id,
            "description": self.description,
            "mode": self.mode,
            "session": self.session or f"ses_{self.id}",
            "steps": [
                {
                    "id": s.id,
                    "kind": s.kind,
                    "args": s.args,
                    "role": s.role,
                    "expect": s.expect,
                    "session": s.session,
                    "gate": s.gate,
                    "tag": s.tag,
                    "note": s.note,
                }
                for s in self.steps
            ],
            "manifest": dict(self.manifest),
        }


def _err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def validate_task(task: TaskDef) -> list[str]:
    """Return validation errors ([] = valid). Used by goldens and the CLI."""
    errors: list[str] = []
    if not task.id or not task.id.replace("_", "").replace("-", "").replace(".", "").isalnum():
        _err(errors, f"invalid task id {task.id!r}")
    if task.mode not in MODES:
        _err(errors, f"{task.id}: mode must be one of {sorted(MODES)}")
    if not task.steps:
        _err(errors, f"{task.id}: at least one step required")

    seen: set[str] = set()
    has_violation = False
    has_evidence = False
    for idx, step in enumerate(task.steps):
        where = f"{task.id}.{step.id or f'#{idx}'}"
        if not step.id:
            _err(errors, f"{task.id}: step #{idx} missing id")
        elif step.id in seen:
            _err(errors, f"{where}: duplicate step id")
        seen.add(step.id)
        if step.kind not in STEP_KINDS:
            _err(errors, f"{where}: unknown kind {step.kind!r}")
        if step.role not in ROLES:
            _err(errors, f"{where}: unknown role {step.role!r}")
        if step.expect not in EXPECTS:
            _err(errors, f"{where}: unknown expect {step.expect!r}")
        if step.gate is not None and step.gate not in KNOWN_REMOVAL_GATES:
            _err(errors, f"{where}: gate annotation {step.gate!r} is not a known removal gate")
        if step.kind in {"edit", "write", "read"} and not step.args.get("path"):
            _err(errors, f"{where}: {step.kind} requires args.path")
        if step.kind == "edit" and not (
            {"old", "new"} <= set(step.args) or "append" in step.args or "content" in step.args
        ):
            _err(errors, f"{where}: edit requires old/new, append, or content")
        if step.kind in {"bash", "verify"} and not step.args.get("command"):
            _err(errors, f"{where}: {step.kind} requires args.command")
        if step.kind == "omt" and not (step.args.get("tool") or step.args.get("name")):
            _err(errors, f"{where}: omt step requires args.tool")
        if step.role == "violation":
            has_violation = True
        if step.kind in {"verify", "assert"} or step.role == "verify":
            has_evidence = True

    if not has_violation:
        _err(errors, f"{task.id}: at least one role=violation step required")
    if not has_evidence:
        _err(errors, f"{task.id}: at least one verify/assert evidence step required")
    return errors


def validate_all(tasks: list[TaskDef]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for task in tasks:
        if task.id in ids:
            _err(errors, f"duplicate task id {task.id!r}")
        ids.add(task.id)
        errors.extend(validate_task(task))
    return errors

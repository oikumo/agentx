"""B worktree lifecycle - pure composer plus thin git boundary (feature_118).

Session-plane lane on the improvement003 git-plane: claim reserves a sidecar
worktree plus branch, complete is fail-closed on commit/verify/revision, join
merges --no-ff locally then cleans up. The managed 081 lane
(.worktrees / omt prefix) is preserved untouched via lane scoping.

Pure functions (resolve_lane / compose_join / gate_complete) are stdlib-only
with no I/O. status_checks is the single subprocess boundary and fails
closed. No import of state (state imports this module, like workspace).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

SESSION_ROOT = ".sandbox/bench"
SESSION_PREFIX = "feat/"
MANAGED_ROOT = ".worktrees"
MANAGED_PREFIX = "omt/"

__all__ = [
    "LifecycleRefused",
    "SESSION_ROOT",
    "SESSION_PREFIX",
    "MANAGED_ROOT",
    "MANAGED_PREFIX",
    "resolve_lane",
    "status_checks",
    "compose_join",
    "gate_complete",
]


class LifecycleRefused(ValueError):
    """Stable-code lifecycle refusal (code plus human detail)."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code + (": " + detail if detail else ""))
        self.code = code
        self.detail = detail


def resolve_lane(*, task_id: str, generation: int,
                 lane: str = "general") -> dict[str, str]:
    """Lane binding: root plus branch plus path (pure, deterministic)."""
    task = str(task_id or "")
    if not task:
        raise LifecycleRefused("unknown_task", "task_id must be non-empty")
    try:
        gen = int(generation)
    except (TypeError, ValueError):
        raise LifecycleRefused("bad_generation", "generation must be an int")
    if gen < 0:
        raise LifecycleRefused("bad_generation", "generation must be >= 0")
    if str(lane or "") == "managed":
        branch = MANAGED_PREFIX + task + "/g" + str(gen)
        root = MANAGED_ROOT
        path = root + "/" + task + "-g" + str(gen)
        return {"root": root, "branch": branch, "path": path, "lane": "managed"}
    branch = SESSION_PREFIX + task + "-g" + str(gen)
    root = SESSION_ROOT
    path = root + "/" + task + "-g" + str(gen)
    return {"root": root, "branch": branch, "path": path, "lane": "general"}


def _run_git(args: list[str], cwd: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return 1, ""
    return proc.returncode, (proc.stdout or "").strip()


def status_checks(*, path: str, branch: str,
                  base_commit: str) -> dict[str, Any]:
    """Closed git reading for a bound sidecar (thin boundary)."""
    sidecar = Path(str(path or ""))
    if not str(path or "") or not sidecar.is_dir():
        return {"clean": False, "branch_exists": False,
                "commits_since_claim": 0, "head": "unknown"}
    if not str(branch or ""):
        return {"clean": False, "branch_exists": False,
                "commits_since_claim": 0, "head": "unknown"}
    cwd = str(sidecar)
    code, porcelain = _run_git(["status", "--porcelain"], cwd)
    if code != 0:
        return {"clean": False, "branch_exists": False,
                "commits_since_claim": 0, "head": "unknown"}
    clean = porcelain == ""
    code, _ = _run_git(["rev-parse", "--verify", str(branch)], cwd)
    branch_exists = code == 0
    code, head = _run_git(["rev-parse", "HEAD"], cwd)
    if code != 0 or not head:
        return {"clean": False, "branch_exists": branch_exists,
                "commits_since_claim": 0, "head": "unknown"}
    commits = 0
    if str(base_commit or "") and str(base_commit) != "unknown":
        code, count = _run_git(
            ["rev-list", "--count", str(base_commit) + "..HEAD"], cwd)
        if code == 0:
            try:
                commits = max(0, int(count))
            except (TypeError, ValueError):
                commits = 0
    return {"clean": clean, "branch_exists": branch_exists,
            "commits_since_claim": commits, "head": head}


def compose_join(*, tasks: list[dict] | tuple[dict, ...],
                 base_branch: str = "main") -> dict[str, Any]:
    """Pure --no-ff join plan ordered by task_id (no subprocess)."""
    items = list(tasks or [])
    if not items:
        raise LifecycleRefused("empty_join", "no tasks to join")
    norm: list[dict[str, str]] = []
    for i, t in enumerate(items):
        if not isinstance(t, dict):
            raise LifecycleRefused("unknown_workspace",
                                   "task entry must be an object")
        task_id = str(t.get("task_id", "") or "")
        path = str(t.get("path", "") or "")
        branch = str(t.get("branch", "") or "")
        if not task_id or not path or not branch:
            raise LifecycleRefused("unknown_workspace",
                                   "task needs task_id plus path plus branch")
        norm.append({"task_id": task_id, "path": path, "branch": branch})
    ordered = sorted(norm, key=lambda t: t["task_id"])
    commands: list[str] = []
    for t in ordered:
        commands.append("git merge --no-ff " + t["branch"])
    for t in ordered:
        commands.append("git worktree remove --force " + t["path"])
        commands.append("git branch -D " + t["branch"])
    return {"commands": commands, "base_branch": str(base_branch),
            "tasks": [t["task_id"] for t in ordered]}


def gate_complete(*, status: dict, verify_ok: bool,
                  expected_revision: int | None,
                  live_revision: int) -> None:
    """Fail-closed complete gate (returns None or raises)."""
    st = status or {}
    if not st.get("branch_exists", False):
        raise LifecycleRefused("unknown_workspace", "branch not bound")
    if not st.get("clean", False):
        raise LifecycleRefused("unclean_sidecar", "uncommitted sidecar work")
    try:
        commits = int(st.get("commits_since_claim", 0))
    except (TypeError, ValueError):
        commits = 0
    if commits < 1:
        raise LifecycleRefused("no_commit_since_claim",
                               "no sidecar commit since claim")
    if not verify_ok:
        raise LifecycleRefused("verify_red", "suite evidence not green")
    if expected_revision is not None and int(expected_revision) != int(
            live_revision):
        raise LifecycleRefused(
            "stale_revision",
            "expected rev " + str(expected_revision) + " != live rev "
            + str(live_revision),
        )
    return None

"""Worktree execution isolation — feature_081.worktree_execution_isolation
(T5-3 2C, mh8 D11 worktree-per-generation).

Pure path/metadata helpers for the managed-concurrency execution plane.
No import of `.state` (state.py imports this module — the reverse would
cycle); only `.errors` + stdlib, like `lock.py`.

Model (NEXT_STEP §7–§9):
- one current task claim = one ownership generation = one task branch =
  one linked worktree: branch ``omt/<task>/g<gen>``, worktree
  ``.worktrees/<task>-g<gen>/`` under the main-worktree repo root.
- the binding records ``workspace: {id, path, branch, base_commit}`` at
  claim/transfer time (claim IS the coordinator-controlled bootstrap:
  stamping the metadata + best-effort dir/branch creation); result
  submission additionally records ``head_commit`` / ``patch_digest``.
- a stale worker may keep writing its old isolated worktree, but it cannot
  publish: every publish path stays generation-fenced (080), and every
  harness-mediated file edit goes through the containment check
  (``is_path_in_workspace`` — a claim never authorizes edits in the
  integration worktree).

Coordination-root note (§7.1): workers MUST run with OMT_NET_DIR and
OMT_COORDINATION_ROOT both exported at the shared main-worktree bundle
(the coordinator hands them out at bootstrap — the claim envelope carries
the workspace, the env carries the shared root). ``repo_root_for`` derives
the main root from a ``*/.meta/.omt`` bundle dir; anything else is treated
as its own root (hermetic tests use tmp bundle dirs as their own root).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

WORKTREES_DIRNAME = ".worktrees"


def branch_name(task_id: str, generation: int) -> str:
    """Task branch for a generation: ``omt/T17/g3``."""
    return f"omt/{task_id}/g{int(generation)}"


def workspace_id(task_id: str, generation: int) -> str:
    """Workspace id for a generation: ``T17-g3``."""
    return f"{task_id}-g{int(generation)}"


def repo_root_for(base: Path) -> Path:
    """Main-worktree root for a bundle dir.

    ``<root>/.meta/.omt`` → ``<root>``; any other dir is its own root
    (hermetic tmp bundles in tests).
    """
    p = Path(base)
    if p.name == ".omt" and p.parent.name == ".meta":
        return p.parent.parent
    return p


def base_commit_for(repo_root: Path) -> str:
    """Current integration HEAD, or ``"unknown"`` (fail-open, hermetic)."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return "unknown"
    if proc.returncode != 0:
        return "unknown"
    head = (proc.stdout or "").strip()
    return head if head else "unknown"


def workspace_path_for(repo_root: Path, task_id: str, generation: int) -> Path:
    """Absolute worktree dir: ``<root>/.worktrees/<task>-g<gen>``."""
    return Path(repo_root) / WORKTREES_DIRNAME / workspace_id(task_id, generation)


def build_workspace(
    base: Path,
    task_id: str,
    generation: int,
    *,
    repo_root: Path | None = None,
    base_commit: str | None = None,
) -> dict[str, Any]:
    """Workspace metadata for a claim (no FS side effects — see `ensure`)."""
    root = Path(repo_root) if repo_root is not None else repo_root_for(Path(base))
    return {
        "id": workspace_id(task_id, generation),
        "path": str(workspace_path_for(root, task_id, generation)),
        "branch": branch_name(task_id, generation),
        "base_commit": base_commit
        if base_commit is not None
        else base_commit_for(root),
    }


def ensure_workspace(ws: dict[str, Any], repo_root: Path | None = None) -> str:
    """Best-effort coordinator bootstrap: mkdir the worktree dir + a git
    branch at base_commit when a git repo is available. Fail-open — metadata
    is authoritative, the FS is convenience (a missing git never blocks the
    claim; the generation fence, not the directory, is the security
    property, §8.3). Returns the workspace path."""
    path = Path(str(ws.get("path", "")))
    path.mkdir(parents=True, exist_ok=True)
    branch = str(ws.get("branch", ""))
    base_commit = str(ws.get("base_commit", "unknown"))
    if branch and base_commit != "unknown":
        _ensure_git_branch(path, branch, base_commit, repo_root)
    return str(path)


def _ensure_git_branch(
    path: Path, branch: str, base_commit: str, repo_root: Path | None
) -> None:
    """Best-effort `git branch <branch> <base>` — every failure is silent."""
    cwd = str(repo_root) if repo_root is not None else str(path.parent)
    try:
        exists = subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if exists.returncode == 0:
            return
        subprocess.run(
            ["git", "branch", branch, base_commit],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        pass


def is_path_in_workspace(candidate: str | Path, workspace_path: str | Path) -> bool:
    """True iff the resolved candidate lives inside the resolved workspace.

    Non-existent paths resolve fine (strict=False); any resolution error is
    fail-closed (False). Symlinks resolve to their targets — a symlink
    escaping the workspace does NOT pass.
    """
    try:
        cand = Path(candidate)
        ws = Path(workspace_path)
        cand_r = cand.resolve() if cand.is_absolute() else (Path(os.getcwd()) / cand).resolve()
        ws_r = ws.resolve() if ws.is_absolute() else (Path(os.getcwd()) / ws).resolve()
    except Exception:
        return False
    try:
        cand_r.relative_to(ws_r)
        return True
    except ValueError:
        return False

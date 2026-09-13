"""Local transaction authority primitives — feature_079.net_transaction_authority
(T5-1 2A, mh8 D10 lock-first).

One shared advisory-exclusive mutation lock plus a file-backed `command_id`
idempotency index. Every authoritative net/binding mutation path in
`state.py` (fire / splice all modes / sync bootstrap / init_empty) acquires
the SAME lock via `CoordinationLock(...).exclusive()`, and the revision check
runs INSIDE that critical section (the pre-lock check in `cli.py:main` stays
as a fast rejection only — never authoritative, NEXT_STEP §5).

Scope notes (bindings-first, correctness-before-throughput):
- Local-machine only: `fcntl.flock(LOCK_EX)` on `<coordination-root>/net.lock`.
  Advisory — all mutation paths must cooperate (they do: `state._transact`).
  Network/unsupported filesystems fail CLOSED (`lock_unavailable`), never
  silently unprotected. No `fcntl` (non-Unix) also fails closed.
- The lock spans load → check → mutate → save → ledger → command-index
  record. Crash BETWEEN save and ledger is still possible — that is the 3B
  transaction-journal slice, explicitly out of scope here.
- `command_id` index (`net_commands.json`, capped at 500 entries) lives in
  the coordination root so forked/cloned processes share it. Same ID + same
  canonical payload replays the original result (no double-fire); same ID +
  different payload raises `command_id_conflict` (a `SpliceError` from
  `state._transact`, so the CLI envelope path is unchanged).
- `OMT_COORDINATION_ROOT` env overrides the root (forward-compat for 2C's
  shared coordination root); default is the net bundle dir itself.

This module imports only `.errors` (never `.state`) so `state.py` can import
it without a cycle.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .errors import PetriNetError

REPO_ROOT = Path(__file__).resolve().parents[3]

LOCK_FILENAME = "net.lock"
COMMANDS_FILENAME = "net_commands.json"
MAX_COMMANDS = 500
LOCK_TIMEOUT_S = 30.0
LOCK_POLL_S = 0.01


class LockError(PetriNetError):
    """Coordination-lock failure carrying a stable envelope error code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def coordination_root(base: Path) -> Path:
    """Authoritative lock/index dir: OMT_COORDINATION_ROOT or the bundle dir."""
    env = os.environ.get("OMT_COORDINATION_ROOT")
    return Path(env) if env else base


def canonical_hash(op: str, payload: dict[str, Any]) -> str:
    """Stable sha256 over the canonical (key-sorted) command rendering."""
    raw = json.dumps(
        {"op": op, "payload": payload}, sort_keys=True, ensure_ascii=False, default=str
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _commands_path(root: Path) -> Path:
    return root / COMMANDS_FILENAME


def _read_index(root: Path) -> dict[str, Any]:
    path = _commands_path(root)
    if not path.exists():
        return {"commands": {}, "order": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise LockError(
            "lock_unavailable",
            f"command index unreadable at {path} ({exc}) — fail-closed; "
            "remove the file to recover (idempotency history is lost)",
        )
    if not isinstance(doc, dict) or not isinstance(doc.get("commands"), dict):
        raise LockError(
            "lock_unavailable",
            f"command index malformed at {path} — fail-closed; "
            "remove the file to recover (idempotency history is lost)",
        )
    return doc


def lookup_command(root: Path, command_id: str) -> dict[str, Any] | None:
    """Prior commit for command_id, or None. Call only with the lock held."""
    doc = _read_index(root)
    rec = doc["commands"].get(command_id)
    return dict(rec) if isinstance(rec, dict) else None


def record_command(
    root: Path,
    command_id: str,
    canonical: str,
    revision: int,
    result: dict[str, Any],
) -> None:
    """Atomically persist a commit under command_id (pruned to MAX_COMMANDS).
    Call only with the lock held."""
    # TA: why: why (feature_079): the index is the multiprocess idempotency
    # memory — tmp+os.replace under the held lock keeps concurrent recorders
    # from interleaving partial JSON; pruning bounds the file (ledger stays
    # the full audit trail, this is a bounded lookup cache only).
    doc = _read_index(root)
    commands = doc["commands"]
    order = [c for c in doc.get("order", []) if c != command_id]
    order.append(command_id)
    for stale in order[:-MAX_COMMANDS]:
        commands.pop(stale, None)
    doc["commands"][command_id] = {
        "canonical": canonical,
        "revision": revision,
        "result": result,
    }
    doc["order"] = order[-MAX_COMMANDS:]
    path = _commands_path(root)
    root.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


class CoordinationLock:
    """Shared local mutation lock (NEXT_STEP §5.2 `CoordinationLock`)."""

    def __init__(self, root: Path) -> None:
        self.root = root

    @contextmanager
    def exclusive(self) -> Iterator[None]:
        """Hold an exclusive flock for the critical section (fail-closed)."""
        try:
            import fcntl  # noqa: PLC0415 (platform-gated — absent on Windows)
        except ImportError:
            raise LockError(
                "lock_unavailable",
                "fcntl unavailable on this platform — transaction authority "
                "cannot coordinate here (fail-closed, local-Unix scope only)",
            )
        self.root.mkdir(parents=True, exist_ok=True)
        lock_path = self.root / LOCK_FILENAME
        try:
            fh = open(lock_path, "a+b")
        except OSError as exc:
            raise LockError(
                "lock_unavailable", f"cannot open lock file {lock_path}: {exc}"
            )
        try:
            deadline = time.monotonic() + LOCK_TIMEOUT_S
            while True:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise LockError(
                            "lock_unavailable",
                            f"coordination lock {lock_path} still held after "
                            f"{LOCK_TIMEOUT_S:.0f}s — fail-closed (a live holder "
                            "is mid-transaction; retry)",
                        )
                    time.sleep(LOCK_POLL_S)
            yield
        finally:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            finally:
                fh.close()

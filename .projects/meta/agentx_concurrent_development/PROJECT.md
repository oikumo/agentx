# PROJECT: agentx_concurrent_development — Agentx_Concurrent_Development

> Status: **active** · **v0.1 (2026-09-12)** — created by `project.py new`. Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project agentx_concurrent_development`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> Concurrent sidecar development on agentx via git-plane worktrees (main protected; branch feat/<task_id>, gen-fenced claim; net is SSOT, git is derived view).

**Next:** Approve this scope, then spawn first linked feature (`new_feature.py "<name>" --type minor_feature --project agentx_concurrent_development`) — candidate: drift-preview OPT-B backend.

---

## Summary (one line)

Run 2+ agentx dev tasks concurrently in `.sandbox/bench/*` worktrees with net-gated claims and lane-scoped verification/integration.

---

## Purpose

### What this project is

A working agreement + thin automation for concurrent agentx development: net `probe/claim/fire` discipline, `feat/<task_id>` branches, sidecar-only mutation, and join/commit via user.

### What this project is **not**

Not a new scheduler/engine (net stays SSOT); not remote CI; not a replacement for single-task flow when pool is `drained_complete`.

---

## Scope & success criteria

- Scope: 2-worker sidecar runs (worker_slots 2/2 free at rev60); verification + integration lanes (1/1 free); drift-hygiene first (unlinked 11 clearable in 2 links).
- Success: 2 concurrent sidecar tasks claimed/fired/joined without main mutation except via user commit; `invariant` net↔ledger↔git clean; CURRENT_STATE log per task.
- Non-goals: >2 workers, remote push/pull (still denied), auto-merge.

---

## Status

- [ ] First linked feature (header flips draft → active mechanically)

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — <!-- decision -->:** <!-- rationale -->

---

## References

- <!-- anchors, feature dirs, evidence -->

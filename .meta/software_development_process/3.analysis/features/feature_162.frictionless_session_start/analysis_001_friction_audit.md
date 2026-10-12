# Analysis 001 — Session-Start Friction Audit (feature_162)

> Evidence: `ses_ecf04a9c8ffeiBHNnv2ofzQqiZ` (2026-10-12 16:39, `hi`, 5 reasoning blocks 32100B), live `omt_net probe rev0 idle_empty` vs `WORK.compiled.md rev60 NEXT proj:agentx_concurrent_development`, `WORK.md` 94 lines.

## Frictions (cost-ordered)

- **F1 — STALE menu (wrong result):** file `net_rev:60 done=7 NEXT=agentx_concurrent_development` vs live `rev0 empty NEXT=none`. Rule says probe-wins, but menu still rendered A-J from stale file. 17k-token reasoning loop to justify. Root: two truths (compiled file + live marking), no auto-sync/fail-closed.
- **F2 — Empty-live uselessness:** `idle_empty` → `next:none, other:[]`, yet ceremony demands A-J letters. Agent must invent fallback. Root: brief probe has no option descriptors.
- **F3 — Unscoped labels meaningless:** `unscoped:001/002` → `001/002`. Required extra `WORK.md` reads to map to `feature_001/feature_002` (scope unset). Root: IDs without resolved titles in compiled header.
- **F4 — Nav-gate friction:** `grep WORK.md` blocked (doc), fallback to `read`. Startup path should be exempt/pre-indexed. Root: startup not on allowlist.
- **F5 — Ceremony weight for `hi`:** INTRO+GLOBAL(7)+TASKS(10)+SUGGESTED(5) + 3 reads/probes for a greeting. Previous session burned ~70k tokens before any work. Root: no fast-path / lean_start for empty pool.
- **F6 — Pause-tail invisible:** known resume `sandbox/pause_2026-10-12.md (STALE+UC0+bridge+CI+Q5+phantom)` not in Options, only in SUGGESTED prose. Root: Options ≠ resume queue.

## Success criteria (frictionless)

- Single truth: menu built live-first; stale file never renders as picks (fail-closed or auto-sync, 1 tool call).
- `hi` with empty pool → ≤3 lines + 1 letter (or `S`), ≤2 tool calls, unscoped titles resolved.
- Startup path exempt from nav-gate; no extra WORK.md hunts.
- No wrong NEXT: if live `next:none`, say so, don't show file NEXT as NEXT.

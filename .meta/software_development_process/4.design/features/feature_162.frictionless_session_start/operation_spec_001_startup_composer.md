# Operation Spec 001 — Frictionless Startup Composer

> Effortless for the agent: 1 probe → deterministic render, no reasoning loops.

## O1 live_first_menu
- **In:** `omt_net probe max_states=0` brief (`observation/rev`, `menu next/other`, `freshness`).
- **Out:** picks ONLY from live `next/other_enabled`. If live `next:none + other:[]` → zero letters (not stale A-J).
- **Rule:** `WORK.compiled.md` NEVER supplies IDs. Mismatch `file NEXT != live next` → `STALE` banner, probe wins.

## O2 lean_empty_reply (effortless path)
- **Trigger:** `idle_empty + drift:0 + other:[]`.
- **Out (≤3 lines):** `state/rev`, `capacity (workers/lanes/resources free)`, `R=reconcile | ?=detail`.
- **Budget:** ≤2 tool calls (read compiled header + 1 probe, parallel). No WORK.md hunt.

## O3 resolve_titles
- **In:** live menu item `id` (`unscoped:001`).
- **Out:** `title` short (`feature_001 session objectives · scope unset`).
- **Source:** `workc.py` embeds `titles:` in compiled header; composer uses it. No inference.

## O4 startup_read_exempt
- `WORK.md`, `WORK.compiled.md` readable in startup without nav-gate consult. Startup-only, read-only.

## O5 reconcile_offer (no auto-apply)
- STALE → single line `R=reconcile (sync proposal, D4)`. `R` maps to `omt_net sync`, never auto-fired. `S=accept` only when live non-empty.

## O6 git-log as state tool + message compiler (effortless recall)
- **In:** `git log --oneline -N` + `git show --stat HEAD` (read-only, zero reasoning).
- **Out:** last state = last `close(...)/feat(...):` message + `WORK.md` Paused tail. Commits are the encoded project memory.
- **Compiler (worth it, thin):** `scripts/omt/logc.py` — `encode` (HEAD message → `state.json`: project/feature/phase/check/prove) + `decode` (`state.json` → commit subject template `close(proj): … | check N/0 lanes F/P/S`). Startup composer calls `logc.py --last` (1 call) instead of re-reading WORK.md history. No new commit format forced — parses existing `close()/feat()/fix()` subjects, Templates only for new closes.

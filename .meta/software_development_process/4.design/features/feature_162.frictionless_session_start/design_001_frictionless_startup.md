# Design 001 — Frictionless Startup (feature_162)

> Answers analysis_001 F1-F6. Major feature, unlocks `src/` per §12.

## Decisions

- **D1 live-first, fail-closed:** startup composer reads ONLY `omt_net probe max_states=0` for picks. `WORK.compiled.md` is context, never picks. If `NEXT mismatch` → banner `STALE — live:none` + zero stale letters, offer `R=reconcile` (single `sync` proposal), not A-J.
- **D2 lean empty-pool fast path:** if `idle_empty + 0 drifts` → 3-line reply (`state/rev`, `capacity`, `R=reconcile | ? detail`), no 10-item menu. Full menu only when live `other_enabled/next` non-empty.
- **D3 resolved titles in probe:** extend brief menu items with `title` (unscoped → `feature_001 …` short title). No WORK.md hunt. Fallback: `001 · scope unset` (honest, no inference).
- **D4 startup nav exemption:** whitelist `WORK.md`, `WORK.compiled.md` for startup composer (read-only, no consult tax). Document as startup-only, not general bypass.
- **D5 resume queue as first-class option:** if pause note lists resume work, surface as single `R` line (not prose). No invented IDs — `R` maps to `sync`/`reconcile`, D19-exempt advisory only.

## Changes (thin slice)

- `src/agentx/` startup composer (TBD module — locate via KB `TIER_CODE` on implement): new `live_first` branch + lean renderer.
- `.opencode/plugins/omt_net.ts` (if owned): include `title` in brief menu items (additive, no schema break).
- `WORK.compiled.md` header: add `titles:` line for unscoped (build-side, `workc.py`), backward-compat.
- Tests: `tests/harness_meta/omt/test_startup_frictionless.py` — F1 wrong-menu never renders stale picks; F2 lean path ≤2 calls; F3 titles resolved; F5 token/line budget.

## Non-goals

- No net reset/migration. No new `omt_net` op (closed enum). No question-tool.

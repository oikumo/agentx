# Design 001 — O6c payback metric + run template (shapes)

> Feature: `feature_116.mh11_o6c_wild_payback_measurement` (`minor_feature`) · Phase: Design · Date: 2026-09-20.
> Consumes: Analysis 001 + 093 benchmark design (driver/probe/metrics) + 098 honest-cost + O4 `plan_to_dict` + D1 locked (no `src/agentx/`) + F7 lane-only.

---

## 1. Metric table (093/098 reuse, pure accounting)

Per wild run, one row (CSV + ledger note, no new `net_*` kind):

| col | source | notes |
|---|---|---|
| `run_id, rev, mode` | driver | `mode=sidecar` (pinned worktree) or `fixture`; rev pinned at setup |
| `task_pair` | spec | 2 disjoint tasks (e.g. docs + harness goldens) — same pair runs serial then dispatch |
| `wall_s_serial, wall_s_dispatch` | spawn durations | real `Bun.spawn`/`uv run pytest` time only (setup/pre-warm excluded, per 093) |
| `harness_calls, tool_calls` | transcript | `omt_*` executes + file effects |
| `io_bytes, tokens_est` | transcript | `tokens_est = io_bytes // 4` (mh3 convention) |
| `verify_seconds` | Σ verify spawns | real only |
| `success, regressions` | asserts | missed violations do NOT flip success (093 §unified refusal) |
| `check, build, suite` | `harnessc check` + suite | `check 265/0` + suite N + 2 deselected baseline 1880 held |
| `payback` | derived | `1 - cost_dispatch/cost_serial` per wall + tokens; report both |

No production edits: driver/probe run from live `.opencode` via `initOmtShared(sandbox)` (093 gotcha); `.opencode/`, `opencode.jsonc`, `.meta/META_HARNESS.omt` untouched.

## 2. Run-log template (CURRENT_STATE + test report)

Each run appends (same file the strategy's results step updates):

```md
### run <id> — <pair> — <date>
- rev: <pinned> · mode: sidecar · workers: ≤2 · lanes: v/i as available
- serial: wall <s>s · tokens <n> · check <a/b> · suite <n>
- dispatch: wall <s>s · tokens <n> · check <a/b> · suite <n> · batch <id> wip <p/a/cap>
- payback: wall <x%> · tokens <y%> · green: held/broken + note
- evidence: transcript <path> · ledger <rev> · CURRENT_STATE link
```

Pilot: first 2 runs (same pair, serial then dispatch) validate the template before N≥10.

## 3. Threshold values (pre-registered, D5)

- **Payback:** median wall ≥15% AND tokens ≥10% over N≥10, zero green loss (`check` 0 + suite green + KNOWN empty every run) → O6a (contract-only) scoped; wall ≥25% AND tokens ≥15% → O6b (full prototype) may be proposed with D1 reversal.
- **No payback:** below either bar, or any green loss, or net-zero/Tier-3 break → defer O6, take WORK.md NEXT `proj:agentx_concurrent_development`.
- **Shape lock:** no new places/transitions (Tier-3); no new ledger kind (reuse `net_claim/net_fire/net_sync` notes); `src/agentx/` untouched; `uv` only; sidecars/worktrees only.

## 4. Receipt + budget plan

- 0 harness-surface edits in Design/Programming (docs + runs only) → no e2e receipt round; any later hermetic pin needs tests/ canary (`omt_skip{scope:tests, purpose:canary}`).
- Token/runtime: N≥10 bounded batches; `.omt @budget work_md` watched — run logs live in CURRENT_STATE/test report, never WORK.md.

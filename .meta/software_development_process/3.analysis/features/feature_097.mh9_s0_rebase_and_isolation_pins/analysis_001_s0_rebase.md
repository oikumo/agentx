# analysis_001 — mh9 S0 rebase + isolation pins (signed at HEAD)

> Feature: `feature_097.mh9_s0_rebase_and_isolation_pins` · type `minor_feature` · phase `Analysis`
> HEAD: `f1be9186e9630c00fa52898c54356782a0410b35` (short `f1be918`) · date 2026-09-14
> Prior baseline in PROJECT.md v0.2 was `06175f0` — this doc re-signs at `f1be918`.
> No `src/` / authority change in S0 (hygiene only).

## 1. Re-verification at HEAD (PROJECT.md §1 → live file:line)

All six residual findings CONFIRMED OPEN at `f1be918` (same lines as `06175f0`):

| ID | File:line at HEAD | Verdict |
|---|---|---|
| F09 durable ack best-effort | `.opencode/lib/omt_shared.ts:154-159` (`appendJsonl` try/catch best-effort) | OPEN — S2 fixes first |
| F02 critical errors fail open | `.opencode/plugins/omt_enforcer.ts:100-103` (rethrow only `OmtBlock`, else warn + allow) | OPEN — S2 must split advice vs authority |
| F05-caller empty→ok | `.opencode/lib/enforcer/phase_gate.ts:455` (`\|\| '{"ok":true}'`) vs `:512` fail-closed pattern (`\|\| '{"ok":false}'`) | OPEN residual (075 closed failing/dangling/coverage `:456-473`, default untouched) |
| F03 one gate stops chain + dry/live divergence | `.opencode/lib/enforcer/gate_driver.ts:219-221` (`g.tests` unconditional `stop`) · chain contract `:366-367` + live break `:349` (`if stop return`) + dry continue-all `:408-410` | OPEN — S2 composes, S3 records parity as UNKNOWN |
| C6 lifecycle ops bypass transition relation | `scripts/omt/net/state.py:296-300` (binding-only lanes) · `:819-834` (`_move_pool_token` direct counters) · `:896` claim path vs `:763-768` fire path (`fire_marking`) | OPEN — no Petri execution guarantee claimable until S5 map (parked) |
| C1 clear-before-record window | `state.py:730-742` (`clear_pending_txn` `:730-734` before `record_command` `:735-742`) vs `:672-675` in-lock marker + `:660-666` reconcile | OPEN residual (084 WAL real progress, window remains) — parked S6a, S0–S4 must not depend on replay surviving window |

Live chain break verified: `runBeforeGates` `:349` returns on `stop`; `runBeforeGatesDry` `:398` marks stop but `:408-410` continues — prediction and enforcement structurally disagree (roadmap F10 shape confirmed).

## 2. Reconciliation table signed at HEAD (PROJECT.md §2)

| Roadmap slice | Assumed (stale `81b3aa1`) | Reality at `f1be918` | mh9 |
|---|---|---|---|
| 1 Task-cost 093 | paused | SHIPPED 17/17 + first-numbers v1 (`3478bb2`, TP=13/FP=0/missed=0, 66 steps, io 140218B) | S1 extends, no redo |
| 2 Truthful F09/F02/F05-caller/F03 | open | 074/075 shipped; four residuals OPEN per §1 above | S2 residual only F09→F05-caller→F02→F03 |
| 3 Thin contract | proposed | 072+073+092 shipped as parts; no single WorkIR | S3 read-only projection, no store |
| 4 Read-only frontier | proposed | not done — highest decision value | S4 paired experiment, gates parked |
| 5–7 Authority/analysis/install | proposed | lanes/locks shipped; C1/C6 + C2–C5 + qual gaps open; 094 advisory shipped | PARKED §4, re-entry gated |

`check` 265/0 + `build` OK re-baselined green at HEAD (warnings only, §3). Suite baseline: 093-era 2231 → 094-era 2241 (S1 re-runs to confirm at HEAD; no claim past that).

## 3. Budget / retirement sheet (headroom at HEAD)

From `harnessc check` at `f1be918`:

| Budget | Used/Cap | Headroom | Diet target if addition lands |
|---|---|---|---|
| tool_args | 2455/2464 | 9B | longest `omt_net arg describes` 657B — free ≥56B or grow cap deliberately same edit |
| tool_schemas | 1840/1856 | 16B | longest `omt_net payload` 376B — free ≥49B same edit |
| agents_md | 2918/2944 | 26B | trim or grow cap deliberately same `.omt` edit |
| nav_index | 64990/65536 | 546B (252 records) | retire one nav record per addition |
| ir_json | 20113/20480 | 367B | retire/compact IR entry same edit |
| gates | 10/12 | 2 slots | net-zero: retire to add |
| work_md | 7683/8192 | 509B | note drift 7641→7683 (+42 since v0.2 draft) |
| work_scratchpad | 1394/3072 | — | — |
| meta_harness_md 1532/2048 · meta_md 5002/6144 | OK | — | — |

Rule (locked): every new tool/gate/nav record ships diet+retirement math in the same edit; Tier-3 excludes net; red check/build/e2e/suite or un-dieted regression → slice reverts, harness untouched.

## 4. Pins (oracle / toolchain / policy / compiler / net-bundle)

- Source: HEAD `f1be9186e9630c00fa52898c54356782a0410b35`.
- Toolchain: python `3.14` (`.python-version`), `agentx 0.2.0`, `pytest 9.1.1` (dev), `@opencode-ai/plugin 1.17.11`, `typescript ^7.0.2`, `@types/node ^26.1.1`; verify commands `uv run pytest …`, `bun *` only; `uv` only (no bare python/pip/pytest).
- Policy: solo-only net, Tier-3 excludes net, KNOWN empty, gates 10/12 net-zero, think/protect + two-hats + genuine-RED + auto-revert + stage discipline hold; mh8 CLOSED 31/31 read-only floor.
- Compiler: `harnessc check` 265 records 0 errors + `harnessc build` OK → 5 projections (ir 20113B, nav 64990B, AGENTS.md 2918B).
- Net bundle: rev **57**, `probe` marking `work_pending=0/active=0/done=7`, `observation=drained_complete`, resources 5/5 free, workers 0/2 used, verification 0/1, integration 0/1; `bindings_valid=true`.
- Oracle (S1 input, UNQUALIFIED today): Done cannot judge its own success; `io_bytes`/`tokens_est` (`//4`)/delivered-bytes/byte-digest are labeled proxies (092: 432B vs ~58KB reread); first-numbers pinned rev `3478bb26f2ce9653ed28ebd567463f21657a622b` ≠ HEAD — S1 must state delta or re-pin before any economy sentence; 6-task/2–3-repeat smoke = variability, not diversity; 20%/30% targets ungrounded.

## 5. Bench corpus freeze + run rules (S1 substrate, no expansion)

Frozen corpus (`task_cost_benchmark.py list` at HEAD): 6 real + 2 fixture.

| task | mode | steps |
|---|---|---|
| bugfix | real | 11 |
| cross_layer | real | 12 |
| major | real | 13 |
| harness_repair | real | 12 |
| resume | real | 7 |
| concurrent_conflict | real | 11 |
| fixture_bugfix | fixture | 10 |
| fixture_nophase | fixture | 7 |

Rules (from `analysis_001_benchmark_design.md`, locked for S1): pinned-rev `git worktree --detach` + fresh gitignored ledger (clean start) + committed `.meta/.omt/{harness.ir.json,nav.index.jsonl}` + net state copied from live + `T-bench` 3-binding injection for concurrent + live `uv.lock` copied before `uv sync` (gitignored, no drift) + `uv sync` pre-warm in SETUP (not counted); paired order + frozen criteria/model/policy pins; cold/warm separation; attempt boundaries recorded; 2–3 repeats max (smoke); no expansion past 6+2–3 without written expansion rule + resource budget; removal experiments are bench-side `irOverride` filters only (zero production flags); sandbox never the live checkout.

## 6. Sidecar-only experiment surface (non-interference)

Default writes: `.projects/meta/meta_harness_9/`, `.sandbox/bench/` (empty, declared), `kb_pilot/` pattern; runs in fresh worktrees/sidecar bundles, never the live checkout. Live surfaces (`.meta/*.omt`, `.opencode/**`, `scripts/omt/net/**`, `tests/`) change only inside a declared slice with approval via stage (snapshot → allow → single e2e → clear) + check/build/suite green before AND after. Authority quarantine S0–S4: nothing authorizes effects or claims verified/managed execution; stale/duplicated/ambiguous refuses + preserves + diagnoses.

## Exit (S0 met)

Signed §2 table (§2 above) + pins (§4) + budget sheet (§3) at HEAD `f1be918`; check/build green; corpus frozen (§5); sidecar declared (§6). Next: S1+S2 as the one allowed pair (disjoint files), then S3, then S4. S5+ stays parked.

# Test Report — feature_130.real_token_discharge

> Task type: minor_feature · sandbox only · 2026-09-26
> Artifacts: `.sandbox/harness_reason/discharge_analysis.md`, `discharge_design.md`, `harvest_ledger.py`, `stage_real_tokens_ledger.json` (NEW) · `run_real_tokens.py` UNCHANGED (f129 baseline digest proves it)

## Verdict

**8/8 PASS ×2 (byte-stable)** with `--ledger` — `REAL_TOKENS_OK 96ba44edc7968ca0`; measured **18/135** rows (6 real sessions × R=3 replay); **unledgered baseline preserved**: `REAL_TOKENS_OK 40e6ab74b10b038a`. Tier-2 gate item (1) is **DISCHARGED with a negative measured reading**: the kernel arm does NOT meet the ≥15% threshold on real H1/H3 medians → runner verdict **`shrink-tier0-or-keep-planner`**.

## What was built (Programming)

- `harvest_ledger.py` (stdlib only, read-only sqlite `mode=ro`): finds child sessions of this project created inside the capture window (`--since` ms), verifies the byte-exact first-line label `^\[harness_reason:discharge arm=(harness|planner|kernel) case=(H1|H3)\]$` on the first user-message text part, enforces exactly-6/one-per-label/zero-unlabeled (else `harvest_label_conflict`, exit 1, **no partial ledger write**), maps `prompt_tokens = tokens_input + tokens_cache_read`, `completion_tokens = tokens_output + tokens_reasoning`, writes the runner-compatible ledger with provenance.
- 6 labeled real capture sessions (Task-tool `general` subagents, labels in prompt first line + description → session title), full prompts per `discharge_design.md` §3.
- `stage_real_tokens_ledger.json`: 6 rows + `provenance` key (runner lookups never match it — loads as "7 rows").

## Live-verified implementation corrections (documented in provenance + TA:)

1. **Label path**: `session_input` table is EMPTY in this DB → used the design §4.3 fallback (first user `message` → first text `part`), which reproduces the known sample `ses_f3eb2547bf*`. The design anticipated this: "both probed live at implementation — pick the one that reproduces the known sample".
2. **Latency units**: session `time_created`/`time_updated` are epoch **milliseconds** → `latency_ms = time_updated - time_created` (design's `× 1000` assumed seconds and would have inflated 1000×).

## Negative test (fail-loudly, pre-capture)

`harvest_ledger.py --since <now>` with 0 candidates → `HARVEST_FAIL harvest_label_conflict` (6 missing labels), exit 1, **no ledger written** ✓.

## Captured sessions (the measured data)

| key | session | prompt_tokens | completion_tokens | total | latency_ms |
|---|---|---|---|---|---|
| harness:H1 | `ses_f204f9861ffeAbWzh4GTXkcRdZ` | 331,490 | 16,882 | 348,372 | 694,124 |
| planner:H1 | `ses_f204f88b3ffeu8NywYtn3PQM1F` | 403,304 | 7,691 | 410,995 | 294,161 |
| kernel:H1 | `ses_f204f7eaaffeOCrWD7pvqgd9M8` | 1,296,107 | 25,622 | 1,321,729 | 1,072,283 |
| kernel:H3 | `ses_f203ed3e2ffeMBDW6z1g3z13AD` | 322,987 | 20,470 | 343,457 | 970,992 |
| planner:H3 | `ses_f203ebe96ffeIOEu7GpsF7sAeP` | 474,389 | 11,656 | 486,045 | 758,150 |
| harness:H3 | `ses_f203eb00dffecktrCSWnhzMfzc` | 358,231 | 23,688 | 381,919 | 1,164,905 |

All six: agent `general`, model `z-ai/glm-5.3` (nvidia, variant max), same project directory, spawned in two batches (H1: harness→planner→kernel; H3 rotated: kernel→planner→harness), window `since_ms = 1790459237218`. Same task text verbatim across arms; arms differed only in the method block (§14.2). All six deliverables returned and all six sessions report repo untouched (verified by git status below).

## Validity checks (`--ledger` run)

| Check | Result | Detail |
|---|---|---|
| V1 shared-inputs parity | PASS | handle H `f7e6b89317420fbd` identical; fork refused |
| V2 oracle agreement | PASS | planner+kernel match harness oracle on T01–T12 |
| V3 unknown discipline | PASS | named unknown, never impossible/proved |
| V4 contract-relative | PASS | (h1,h0) witness for test;edit under completion-relevant |
| V5 reuse freshness | PASS | h2-with-h1 refused with bind location |
| V6 report shape | PASS | 135 rows, measured 18, proxy `mixed`, digest `96ba44edc7968ca0` byte-stable ×2 |
| V7 advisory boundary | PASS | sandbox-only paths; no src/net/toolbox writes |
| V8 span discipline | PASS | every row span-attributed; rewind → `snapshot_inconsistent`; no zero-token measured rows |

## Threshold reading (measured medians — decision rule, not prediction)

Per-arm medians over measured rows (2 distinct real points per arm, each replayed R=3; median sits on the higher case value):

- harness: **381,919** · planner: **486,045** · kernel: **1,321,729**
- reduction vs harness = (381,919 − 1,321,729) / 381,919 = **−2.461** → `meets_15pct_rule: false` → **`shrink-tier0-or-keep-planner`**.

Driver of the reading: the kernel arm's H1 session accumulated ~1.30M prompt tokens — the sandbox-driver calling pattern (re-reading large contexts per kernel op call) is *more* token-expensive than harness/planner discipline in this environment, not less.

## Honest caveats (stated, never silently promoted)

- One capture per (arm, case) replayed across R=3 (f129 documented caveat); medians sit on 2 distinct real points per arm.
- `proxy` stays **`mixed`** — T01–T12 + H2 remain unmeasured; this is a measured reading on the reuse-sensitive cases only.
- Kernel arm drove sandbox kernel scripts (Tier-1 `reason_check` not exposed to subagents) — that is the Tier-0/1 reality being measured.
- Fairness nuance disclosed: all three H3 arms independently chose to mutate `stage0_ir.json`; two bumped `ir_version`, one resolved the d3 binding (task text left the mutation choice open; work shape comparable across arms).
- Small pilot; variability note unchanged ("small pilot proves nothing universal").

## Regression suite (gate-review discipline)

| Suite | Result | Digest |
|---|---|---|
| run_real_tokens.py `--ledger` ×2 | 8/8 PASS | `96ba44edc7968ca0` stable |
| run_real_tokens.py unledgered | 8/8 PASS | `40e6ab74b10b038a` (f129 baseline — runner unchanged) |
| S0 run_probes.py | 7/7 PASS | `6e355d7189e13fb5` stable |
| S1 run_checker.py | 12/12 PASS | — |
| S2 run_composer.py | 7/7 PASS | — |
| S3 run_experiment.py | 7/7 PASS | `d476df80d71d829a` unchanged |
| tier0_demo.py | PASS | — |
| tier1_demo.py | PASS | — |
| tests/scripts/reason/ | 14 passed | — |

## Boundary check

`git status` shows only `.projects/meta/META.md` + `WORK.md` (pre-existing project-home sync), `.meta/.../feature_130.real_token_discharge/`, `.sandbox/harness_reason/{discharge_analysis.md,discharge_design.md,harvest_ledger.py,stage_real_tokens_ledger.json}` — no src/tests/net/toolbox change from this feature or any of the 6 capture sessions (advisory boundary holds).

## Reading for the Tier-2 gate

- Item (1) real-token measurement: **discharged — threshold MISSED on the measured reuse-sensitive cases** (kernel −246% vs harness, not +15%). Per the §15.6/§15.1 kill line and D6 (fair comparison decides): the measured evidence recommends **keeping Tier-0/1 and shrinking rather than promoting `omt_reason.ts`**; the enhanced typed planner (A1) also did not beat the harness arm on these medians, so the honest measured ranking is harness ≈ planner < kernel-on-sandbox-drivers.
- Gate items (2) budgets w/ harness-surface cost, (3) `omt_reason.ts` surface, (4) user-selected implementation remain open in form, but promotion now lacks a positive measured case — re-convene the gate to record the negative reading and close Tier-2, or archive if Tier-0/1 is deemed terminal.

# Analysis 005: Evaluation Plan — Think Anywhere (feature_021 + feature_022)

> **Status:** Plan — awaiting approval to execute
> **Created:** 2026-07-18
> **Scope:** Post-shipment evaluation of the Think-Anywhere subsystem: feature_021 (v1) and
> feature_022 (v2, all tiers: A, B1+D1, C, B2+E1+E2).
> **Precedent:** feature_022 itself originated from a post-mortem evaluation of feature_021;
> this plan evaluates *both* the shipped subsystem and the quality of that prior evaluation.

---

## 1. Purpose

Answer, with evidence:

1. **Claims coverage** — Does the shipped code do what FEATURE.md + tier docs claim?
2. **Flaw resolution** — Are the 13 flaws (F1–F13) that motivated v2 actually fixed?
3. **Intent gap** — Did v2 restore the paper's load-bearing mechanics (entropy-guided
   placement, outcome validation, point-of-use delivery), or only the aesthetic?
4. **Test integrity** — Do the claimed ~100 tests exist, pass, and test the right things
   (not vacuous / over-mocked)?
5. **Live behavior** — Does the subsystem behave as documented *empirically* (digest,
   think-gate, read-injection, verify/stale lifecycle, suggest, reindex)?
6. **Adoption & net value** — Is the feature used, and is it worth its friction cost
   (think-gate blocks, e2e-receipt churn recorded in WORK.md gotchas)?
7. **Prior-evaluation quality** — Was the 021→022 post-mortem itself sound (were its
   13 findings real, correctly prioritized, and completely addressed)?

## 2. Evidence base (inventoried 2026-07-18)

| Source | Size | Role |
|---|---|---|
| feature_021 phase docs (req/analysis/design/impl/test) | 733 lines, 6 files | Claims |
| feature_022 phase docs (4 tiers × 5 phases + FEATURE/PLAN) | ~2,438 lines, 22 files | Claims |
| Theory doc `.meta/doc/harness/think_anywhere_langchain.md` | 13 KB | Intent-gap baseline |
| `.opencode/plugin/omt_think.ts` | ~800+ lines | Implementation |
| `.opencode/plugin/omt_enforcer.ts` (think-gate, digest, D1 hook) | — | Enforcement |
| Tests: `test_omt_think.py` (30) + 4× v2 modules (15/17/22/16) | 1,846 lines, 100 tests | Test claims |
| E2E: `test_omt_harness_e2e.py`, `test_omt_lifecycle_e2e.py` | — | Live plugin proof |
| `.meta/.omt/thoughts.jsonl` | 105 records | Index health |
| Live census: 6 `TA:` thoughts across 3 files | — | Adoption |
| `.meta/.omt/ledger.jsonl` | — | Process conformance (phase/skip audit) |
| WORK.md gotchas | — | Friction cost |

## 3. Method — phased execution

### P0 — Recon ✅ (done, this inventory)

### P1 — Claims extraction (doc review, no repo mutation)
- Read all 28 feature docs + theory doc; build a **traceability matrix**:
  `claim → source doc:line → verification method → evidence → verdict`.
- Rows: every F1–F13 fix, every tier operation (A1–A4, B1, B2, C1, C2, D1, E1, E2),
  v1 guardrails (deny list, caps 30/50, no-skip-bypass), intent-gap table rows.
- Output: matrix skeleton with ~40 claims.

### P2 — Test verification (execution, no repo mutation)
- Run: `uv run pytest tests/features/feature_021.* tests/features/feature_022.* -q`
  → confirm 100/100 and compare against test-report claims per tier.
- Run harness set: `uv run pytest tests/scripts/omt/ -q` → confirm 246/246 claim.
- Refreshes the e2e receipt as a side effect (harmless, routine).
- Spot-audit 5–8 tests for vacuity (assert real behavior, not mocks of themselves);
  check node-runner tests actually exercise the TS plugin, not a reimplementation.

### P3 — Static code review (read-only)
- Verify each mechanism exists as designed in `omt_think.ts` / `omt_enforcer.ts`:
  anchored gate regex (A1), extension deny/map (A2), string-guard (A3),
  category-lowercase/query-escape/dedup (A4), anchor+symbol resolution (B1),
  AST suggest ranking (B2), verify/stale index records (C1), per-file consult (C2),
  read-time injection hook (D1), reindex idempotence (E1).
- Note any undocumented behavior or dead code. Cross-check the accidental anchored
  `TA:` at `omt_enforcer.ts:~1026` is intentional/harmless.

### P4 — Empirical probes (controlled, live-fire)
Read-only on live files: `omt_think_list`, `omt_think_suggest` (suggest is read-only).
State-mutating probes **only on temp copies** under `/tmp/opencode/think_eval/`:
- insert via `after:`/`symbol:` anchors → confirm placement + index record (B1, A3);
- insert into triple-quoted string / unknown extension → confirm refusal (A2, A3);
- duplicate insert → confirm dedup (A4);
- `omt_think_verify` on a live thought → confirm verified record appended (C1;
  acceptable: appends one JSONL record, does not touch source files);
- `omt_think_reindex` → run, confirm idempotent (run twice, diff) (E1);
- gate false-positive check: grep `TA:` prose files (e.g. feature_001 consortium doc)
  no longer gate (A1/F3);
- D1 read-injection: read a thought-carrying file and confirm injection appears.
- Backup `thoughts.jsonl` before probes; restore after if anything beyond the
  accepted verify-record drifts.

### P5 — Adoption, friction & process audit (read-only)
- Census analysis: 6 thoughts — category spread, placement quality, verified/stale
  state; is 6 thoughts across ~2 days evidence of adoption or of cost?
- Index health: 105 records vs 6 live thoughts — drift/zombie rate; E1 effectiveness.
- Ledger audit: count `omt_skip` events related to think features; TDD two-hats
  violations (should be 0); phase declarations per tier present.
- Friction ledger: WORK.md gotchas attributable to 021/022 (receipt churn, think-gate
  on own files, Write-tool chunking) — cost vs. benefit judgment.

### P6 — Synthesis
- Score each matrix row: ✅ verified / ⚠️ partial / ❌ contradicted / ❓ unverifiable.
- Answer Q1–Q7 with evidence citations.
- Findings list (new flaws found, if any, F14+), prioritized like the v2 FEATURE.md.
- Recommendations: keep/fix/remove per mechanism; net-value verdict.

## 4. Deliverable

`6.testing/features/feature_022.meta_harness_think_anywhere_v2/evaluation_001_post_shipment.md`
— full matrix + findings + scores. (Naming follows the `NNN_topic` convention; a
retrospective evaluation is a testing-phase activity.)

## 5. Boundaries & safety

- No edits to `src/`, no edits to guarded files (`.opencode/plugin/*.ts`, `opencode.jsonc`).
- No new `TA:` thoughts in repo files; mutations only in `/tmp/opencode/think_eval/`.
- `thoughts.jsonl` backed up before P4; only C1 verify-records accepted as permanent drift.
- No `omt_done` (known-unreachable per WORK.md); no commits.
- Evaluation itself is a `docs`/`test`-class activity: no `omt_phase` needed (no `src/` edits).

## 6. Effort & sequencing

| Phase | Effort | Depends on |
|---|---|---|
| P1 claims extraction | ~40 min | — |
| P2 test runs | ~10 min | — |
| P3 code review | ~40 min | P1 (matrix rows) |
| P4 probes | ~30 min | P3 (know what to probe) |
| P5 adoption/process | ~20 min | — |
| P6 synthesis | ~30 min | all |

P1+P2 can start in parallel; P3/P5 independent; P4 after P3; P6 last.
Single-session total: ~2.5–3 h.

## 7. Open decisions (defaults assumed unless overridden)

1. **Depth:** full audit (default) vs. quick health-check (P2+P4+P6 only).
2. **Report location:** `6.testing/.../evaluation_001_post_shipment.md` (default) vs.
   `.meta/doc/harness/` as a standalone harness-evaluation doc.
3. **C1 verify probes** append permanent records to `thoughts.jsonl` (default: accept).

# Design 003 — S6 acceptance (live verification + pilot + Tier-2 hardening)

Feature: `feature_131.opencode_session_inspection_and_experiments` · Phase: Design · Date: 2026-09-27
Inputs: `design_001` (core S1–S4) · `design_002` (Tier-2 S5) · PROJECT.md §acceptance AC1–AC12 · live census 2026-09-27 (1857 sessions / 47k messages / 195k parts; agentx 1724 / 42k / 177k) · `MH13_LIVE_DB=1` 50 passed.

## 1. Goal

Close feature_131 with measured AC1–AC12 evidence through the registered `omt_session` tool. No new capability, no second scheduler, no `src/agentx/` dependency. Two S5 hardening fixes are in scope (AC10 blockers); the 12-trial pilot runs only on explicit approval.

## 2. Live baseline (measured 2026-09-27, read-only, no bodies dumped)

- Corpus: full DB 242k records (47k messages + 195k parts) — AC3 ≥100k satisfied by agentx parts alone (177k).
- AC1 shapes: ordinary dev `ses_0a85d1b6cffeOC` (68M tokens top-cost) · failure/retry `ses_0eaa78cd4ffeHR` (29M + 229 error-like parts) · parent/child 85/1724 sessions with parent_id.
- AC2 candidates overlap top-cost/error sets (`ses_0a85`, `ses_0eaa`, `ses_0ac6`, `ses_0cc2`).
- A2 reasoning reconciliation: env-gated live tests green (50 passed, 102s directory scan).

## 3. AC1–AC5, AC9, AC11 verification (read-only, bounded)

| AC | Method (bounded, no full scan per call) |
|---|---|
| AC1 | One session per shape via `session_ids=[...]` snapshot + normalize + hierarchy forest; coverage gaps explicit. |
| AC2 | Costly session → `profile.hotspots` ranking → `inspect.get_part` paged drill-down → `trace.timeline` surroundings; unavailable reasoning stays unavailable. |
| AC3 | Typed `query` + `top_cost` across agentx corpus with limit/cursor; pagination completeness asserted (no missing/duplicates); cold/warm latency + memory reported separately; resource-limit failures named (`query_limit_exceeded`, `cursor_stale`). |
| AC4 | `usage.reconcile_session` on reasoning-bearing live sessions (A2); disjoint vs output_includes_reasoning variants; residual exposed, never smeared; valid zeros kept. |
| AC5 | `event_cursor` re-read on an active session: stable IDs, versioned digest, idempotent replay, explicit incomplete coverage, source DB unchanged (`mode=ro` asserted). |
| AC9 | `exporter.export_bundle` → `replay_bundle` digest equality without model calls; source refs navigable. |
| AC11 | Default summaries ≤2 KiB + `detail_ref`; large bodies paged; instrumentation overhead measured separately from trial cost. |

All calls use `session_ids` or `directory + time_from/time_to + limit` bounds. Unbounded directory scans are dev-only; the Tier-2 path refuses or pages them with a named finding (never silent truncation).

## 4. S5 hardening fixes (AC10 blockers, in scope)

**B1 — stdlib shadow:** plugin runs `uv run scripts/session_inspect/service.py <op>` as a script, putting `scripts/session_inspect/` on `sys.path[0]`; `inspect.py` then shadows stdlib `inspect` and `argparse` crashes (reproduced 2026-09-27). Fix (both, defense in depth):
- (a) Rename canonical module `inspect.py` → `detail.py` (op enum string `inspect` unchanged); keep NO `inspect.py` file on disk (shadowing persists while any such file exists). Update the 2 test imports + `__init__` surface doc. TDD same-node discipline per S2 precedent (no deletions that orphan REDs — migrate imports in the GREEN step).
- (b) Plugin launches `uv run python -m session_inspect.service <op>` with cwd `scripts/` context (or repo root + PYTHONPATH) so script-dir shadowing cannot recur. Pin cross-source argv parity test still green.
- Regression: new test asserts `service.py`-as-script CLI exit 0 on a fixture DB (would have caught B1) + whitelist/parity pin re-run.

**B2 — timeout vs scan:** plugin 30s timeout vs ~100s live directory scan. Fix:
- Plugin timeout 30s → 120s for read ops (`run` stays refused pre-dispatch, unaffected).
- Bounded-directory rule: directory selector without `time_from/time_to` gets a default recent window + `limit` cap in the Tier-2 dispatcher (dev CLI keeps explicit behavior); over-budget queries return `query_limit_exceeded` with resume cursor, never a bare timeout.
- Report cold/warm latency on the 242k corpus in the test report.

Harness-surface discipline: plugin `.ts` + `.omt` (if touched) follow receipt round-robin (ONE edit per file per e2e receipt, pin-tests first, `.omt` LAST). `scripts/session_inspect/*` are NON-harness — keep the delta there where possible. `feature_129/130` scripts untouched; fixtures synthetic only.

## 5. 12-trial pilot (AC6–AC8, AC12) — plan only, NO launches in this design

- Matrix: 2 variants (baseline/candidate prompt strategy) × 2 cases (markdown-summary, python-fix in `/tmp` isolation, digests pinned) × 3 independent reps = 12 trials, order seed recorded, models/settings/budgets pinned, outcome checks independent of end markers.
- `manifest.dry_run` renders: exact trial matrix, `[mh13.experiment]` label lines, execution commands, isolation paths, resource bounds, collection selectors, expected labels — `executed: False`, no OpenCode launches, no tokens.
- Negative battery (AC7, synthetic, no launches): duplicate/conflicting labels, missing/aborted trials, wrong variant/rep, contamination, drifted inputs/models, orphan/reversed spans, spoofed echoes, resumed attempts — each excluded with reason.
- AC8: one nested-span/child-session trial shows supported vs `span_usage_unavailable` attribution; legacy feature-130 labels import without invented reps.
- AC12: quality-gated comparison (cheaper failures never win); predeclared decision rule returns supported conclusion or explicit inconclusive.
- Execution awaits explicit `p` approval + isolation/budget confirmation; replay never increases N.

## 6. TDD / verification list (S6)

1. `s6.b1_no_shadow` — script-launch CLI green on fixture DB; `python -m` launch green; parity pin green.
2. `s6.b2_bounded` — over-budget directory query returns `query_limit_exceeded` + cursor; session_ids drill-down within timeout; cold/warm numbers recorded.
3. `s6.ac1_ac5_live` — env-gated (`MH13_LIVE_DB=1`): 3 shapes, hotspot→part→trace chain, reconcile, re-capture idempotence.
4. `s6.ac3_bench` — ≥100k corpus pagination completeness + latency/memory split.
5. `s6.ac9_replay` — export→replay digest stable, no model calls.
6. `s6.pilot_dry_run` — 12-trial manifest dry_run renders 12 label sets, `executed: False`, negative battery excluded with reasons (no launches).

Exit: test_report Addendum S6 + full `uv run pytest -q` + `harnessc check` 0 errors + fresh e2e receipt (if harness-surface touched) + CURRENT_STATE S6 entry + one auditable report bundle. Then `omt_complete` Testing→Done.

## 7. Non-goals

No unrecorded-reasoning reconstruction, no theorem engine, no auto policy/src changes from diagnoses, no second scheduler, no GUI, no remote log services, no pilot launches without `p` approval.

# Round 004 — Package 3: policy acceptance (AXR-03)

> Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (override — no OMT gates for this run; `omt_think` + mocked tests + approval gate still apply).
> Project: `agentx_1_0_0` (draft) — repair-only, order 1→6, acceptance = per-finding Regression check.
> Scope source: `sandbox/consistency_enforcement/round_001_implementation_review.md` §AXR-03 + 4 probes (`test_axr03_stale_and_invalid_replacements`, `rejected_first_insertion_seeds_cache`, `replacement_conflicts_with_itself`, `failed_persistence_publishes_live_rule` — all assert faulty).
> Step: strategy 3 (propose) — STOP at step 4 approval gate. No `src/` edits applied in this round.

## 1. Confirmed gaps (summary, `evaluator.py`)

- `_compile` caches by rule ID, never invalidates: `true`→`false` replacement keeps matching `true`; `@@invalid@@` replacement accepted without compiling (validation reuses cache).
- `add_rule_safely` conflict check runs against `rules + [candidate]` **including the superseded same-ID version** → legit action-only replacement self-conflicts (score 1.0, rejected).
- Complexity guard runs **after** compile+cache: rejected 11-param first insert seeds `_compiled`, later valid same-ID attempt matches stale `true`.
- Premature publication: `add_rule` sets `rules[id]` then `repository.save`; injected `OSError` leaves the live rule active and matching (persisted vs live disagree).
- Same contract must cover direct `add_rule`, repository reloads, and `revert_rule` rollback (rule + compiled expression restored together).

## 2. Alternatives (pick one)

- **A* — one success/failure contract (recommended, report recipe).** Shared `_validate_candidate`: fresh compile into a throwaway (never touches `_compiled`) → complexity guard → conflict check vs the **final** set (same-ID old excluded) → `repository.save` → publish `rules[id]` + `_compiled[id]` together. Any failure (compile, guard, conflict, save) leaves prior rules/compiled/persisted state untouched. Applies to `add_rule` and `add_rule_safely`; `revert_rule`/`load_from_repository` ride the same path (rollback restores both rule and expression).
- **B — validation reorder only (partial).** Always recompile on condition change + run the complexity guard before caching, fix self-conflict exclusion — but keep set-then-save order. Cures stale-cache/self-conflict, still publishes live on persistence failure.
- **C — safe-path-only fix.** Apply A inside `add_rule_safely` only; leave direct `add_rule` (load/rollback callers) on current semantics. Faster, splits the contract the finding explicitly unifies.

### Cross-cutting (any pick)
- Acceptance: `true`→`false` stops matching now; invalid replacement fails + previous intact; rejected first insert inert for later same-ID attempt; legit action swap passes while genuine cross-rule conflicts still fail; rollback restores rule+compiled; save failure publishes nothing.
- Mocked tests: failing-repository double + in-memory replacements (no DB); rollback case included.
- Probe retired, not gated (D4).

## 3. Approval gate (step 4 — awaiting user)

Reply with a single letter (A/B/C). No `src/` edits until go-ahead (step 5). Results go to `# Result` below after execution (step 6).

## 4. Execution notes (for step 5, after approval)

- Mocked unit tests first (rule 3); `omt_think` in touched source (rule 2).
- Record: repaired revision, test nodes/commands, coverage, residuals.

# Result (executed 2026-09-20 — user picked A)

- **Chosen:** A (one success/failure contract). `evaluator.py`: `_compile_fresh` (throwaway compile, never touches `_compiled`); `add_rule` = fresh-compile → save → publish rule+compiled together (raises before publishing); `add_rule_safely` = fresh-compile → complexity guard → conflict check vs final set (same-ID old excluded) → save (raises, publishes nothing) → publish together; `load_from_repository` fresh-compiles per rule, skips uncompilable (logged); `_compile` recompiles on expression drift. Direct `add_rule` keeps no conflict/complexity gate (trusted/load/rollback path) but shares atomic save-then-publish. `omt_think` added.
- **Observation probes (must stop passing):** all 4 axr03 probes **FAIL as desired** — stale-replacement now PAUSE (not stale EXECUTE), rejected-first-insert inert, legit action swap accepted (`assert not True` fails), failed-save publishes nothing.
- **Regression proof (this session):** replacement-applies, invalid-rejected-intact, rejected-first-inert, noselfconflict-plus-realconflict (genuine cross-rule PAUSE-vs-EXECUTE still score 1.00 rejected), save-failure-clean, rollback-restores-rule+compiled — all PASS.
- **Existing suites:** `polic|conflict|proposal|reflect` **91 passed** (incl. `test_policy_engine.py` direct-`add_rule` callers and snapshot-restore H3/H7 paths).
- **Residuals:** direct `add_rule` intentionally ungated on conflicts (conflicts surface via `resolve_conflicts`); reload skips (never auto-repairs) uncompilable persisted rules.
- **Next:** Package 4 session lifecycle (AXR-04, AXR-08, AXR-09). Do not close Package 3 until durable `tests/` regressions land (canary approval needed). CLOSED 2026-09-20: 6 durable tests landed in `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr03_policy_acceptance.py` (canary).

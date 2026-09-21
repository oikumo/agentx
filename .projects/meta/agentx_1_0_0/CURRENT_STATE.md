# CURRENT_STATE: agentx_1_0_0

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-20 (iter 11 — v1.0.0 RELEASED)

### Done

- Release declared (user-approved): PROJECT.md header draft → active, release-gate + first-linked-feature boxes checked.
- Release evidence: 6/6 packages executed + proven + closed; 48 durable regression tests (5+4+6+9+8+16); 20/20 observation probes fail as desired, retired per D4 (sandbox-only review artifacts); full suite 1972 passed, 0 failed; ReAct collection restored (exclusion removed, 2 stale-API modules deleted); docs reconciled (7 edits, feature_007/013/019/027).
- Residuals carried forward (out of 1.0.0 scope per D1): AXR-11 `send_message` still re-raises cycle exceptions (busy released, REPL loop dies — separate product decision); `max_active_goals` default stays 10 as reserved cap; C-extras deferred (centralized `ensure_conversation`, `_refl_repo.save`/`persist()` guards, all-validator type checks, `ActionType.PAUSE` implementation); new defects found post-release become 1.0.1 candidates.

### In progress / Blocked

- _(nothing — release complete; tree left uncommitted per policy: commit only on explicit request)_

### Next

- 1.0.1 candidates (if new defects surface); commit on request.

---

## 2026-09-20 (iter 10 — docs reconciliation pass, last release-gate item)

### Done

- Reconciled design examples with repaired behavior (7 edits, no code changes): feature_019 OP-5 File Edit example → mkstemp O_EXCL + os.replace + perm preserve (AXR-01); feature_027 op-spec chunk-analyst → `backend_path` contract; feature_027 design → per-invocation `search_id` naming + collision risk marked RESOLVED; feature_027 implementation_notes → repaired dataclasses + error boundary; feature_007 data dictionary → `maxActiveGoals` reserved cap; feature_007 NFR → 1 active goal enforced; feature_013 Flow 2 → lazy-refresh + per-request binding lifecycle contract (AXR-06).
- Verified: no stale `chunk_0.txt` contracts or concurrent-goals statements remain in `.meta` (only sandbox history + the new reconciled text).

### In progress / Blocked

- _(nothing — release gate review is the only remaining step)_

### Next

- Release gate review: all regression checks green (48 durable tests), probes retired 20/20 (D4), suite green (1972), ReAct collection restored, docs reconciled.

### Notes / context

- Docs are non-gated (no canary needed); class diagram `+maxActiveGoals: int` left untouched (field still exists — accurate).

---

## 2026-09-20 (iter 9 — ReAct collection restored, release-gate item)

### Done

- Removed stale `tests/conftest.py` `pytest_ignore_collect` blanket exclusion (canary logged); deleted 2 stale-API modules importing never-existing `ReActController`/`ReActView` (`tests/controllers/react_controller/`, `tests/views/test_react_view.py`) — DELETE chosen over rewrite: they tested a planned-but-never-implemented API while the real surface is covered by feature_018 (16 tests) + feature_024 console parity.
- Verified: `feature_018/test_react_controller.py` 16 tests now collect through the normal `tests/` path; full suite **1972 passed, 0 failed** (1956 + 16).

### In progress / Blocked

- feature_027 design-doc examples still show bare `chunk_0.txt` (docs reconciliation pass pending) — last release-gate item besides the gate itself.

### Next

- Docs reconciliation pass, then release gate review (all regression checks green ✓, probes retired ✓, suite green ✓, ReAct restored ✓).

### Notes / context

- `test_kb_pilot.py` references only the react_view.py *path string* in test data — unaffected by the deletion.

---

## 2026-09-20 (iter 8 — pkgs 1–5 durable regressions landed, all packages closed)

### Done

- Reconstructed inline proof from round_002..006 as durable tests (5 parallel drafting subagents, tree-verified APIs; canary logged): pkg 1 = 5 tests (`feature_019/test_axr01_axr02_axr12_filesystem_containment.py`), pkg 2 = 4 (`feature_024/test_axr06_provider_dispatch.py`), pkg 3 = 6 (`feature_007/test_axr03_policy_acceptance.py`), pkg 4 = 9 (`feature_007/test_axr04_axr08_axr09_session_lifecycle.py`), pkg 5 = 8 (`feature_027/test_axr05_rag_file_handoff.py`).
- Verified: all 32 pass on landing; full suite **1956 passed, 0 failed** (1924 + 32; 2 deselected = pre-existing `opencode_live` marker).
- Closed pkgs 1–5 in PROJECT.md + round_002..006 docs (closure lines with file paths).

### In progress / Blocked

- ReAct collection restoration (release-gate): `tests/conftest.py` blanket exclusion still hides passing feature_018 tests + 2 stale-API modules — needs tests/ canary + delete-vs-rewrite decision.
- feature_027 design-doc examples still show bare `chunk_0.txt` (docs reconciliation pass pending).

### Next

- Release-gate closure: ReAct restoration decision, docs pass. All 6 packages executed + proven + closed; 20/20 probes retired (D4).

### Notes / context

- Drafting pattern that worked: parallel explore subagents returned complete modules + API-mismatch risk lists; all 32 passed unmodified on first run — tree-verification in the prompt paid off.
- LSP "unresolved import / unknown attribute" diagnostics on the new test files are venv-visibility + Optional-inference noise; runtime green is the arbiter (same pattern as the probes).

---

## 2026-09-20 (iter 7 — package 6 executed, combo A+B+B)

### Done

- Executed AXR-07 repair (A lazy): idempotent system-prompt guard + conversation creation at first completed round in `process_user_message` (raw `history_repo.create_conversation`, AXR-06 request identity; `start_new_conversation` not reused — clears history); reopen path untouched (D5).
- Executed AXR-10 repair (B centralized): `_enforce_single_active` choke point — vacancy-gated promotion (`was_active` + no active), focus-switch activation, pre-ACTIVE insertion demotion, revert enforcement, repository load heal+persist; `max_active_goals` documented as reserved cap.
- Executed AXR-11 repair (B boundary + recovery): `validate` inside `execute_safely` try + warning log; filesystem path type check; `run_cycle` conditional `finally` (preserves PAUSED/TERMINATED, re-raises).
- Verified: **20/20 observation probes fail as desired** (census 18/2 → 20/0); **16 regression scenarios PASS** (`/tmp/opencode/pkg6_regression.py`); full suite **1908 passed, 0 failed**.
- Proposal + evidence: `sandbox/consistency_enforcement/round_007_package_06_conversation_recovery.md` §Result.

### In progress / Blocked

- **Package 6 closed:** 16 durable regressions landed in `tests/` (feature_024 `test_axr07_chat_persistence.py`, feature_007 `test_axr10_single_active_goal.py` + `test_axr11_safe_execution_recovery.py`); full suite 1924 passed (1908 + 16).
- Durable `tests/` regressions for pkg 1–5 still pending (canary) — those packages not closed until landed (their proof was inline-only).
- ReAct collection restoration (release-gate): `tests/conftest.py` blanket exclusion still hides passing feature_018 tests + 2 stale-API modules (`ReActController`/`ReActView` never existed) — needs tests/ canary + delete-vs-rewrite decision.
- feature_027 design-doc examples still show bare `chunk_0.txt` (docs reconciliation pass pending).

### Next

- Release-gate closure: durable regressions canary, ReAct restoration decision, docs pass.

### Notes / context

- Parallel sub-agent analysis (3 findings) → proposal doc → user approved recommended A+B+B → execution.
- `send_message` still re-raises cycle exceptions (B+ catch excluded): busy released but REPL loop dies — intentional, separate decision.
- Approval + combo details: `round_007_package_06_conversation_recovery.md` §2–3.

---

## 2026-09-20 (iter 6 — package 5 executed, "do it all")

### Done

- Executed AXR-05 repair ("do it all" approval; D6 keep-delegate): unique absolute `/retrieval/<search_id>/chunk_i.txt` keys, backend wired through `build_rag_v2_tools` + service, structured error boundary (factory/call/upload), per-file `upload_errors`, honest `chunks_uploaded`, `RagSearchHit.backend_path` + prompt agreement.
- Verified: 5/5 axr05 probes fail as desired; 8 acceptance scenarios PASS (real-graph analyst reads, sequential/parallel no-overwrite, partial/failed uploads, empty-vs-failure, exceptions); `rag|retrieval|chunk|backend|subagent` 135 passed.
- Reconciled `test_rag_v2_retrieval_tool.py` to the new path contract (tests canary logged — report-directed).
- Proposal + evidence: `sandbox/consistency_enforcement/round_006_package_05_rag_file_handoff.md` §Result.

### In progress / Blocked

- Durable `tests/` regressions for pkg 1–5 (canary) — packages not closed until landed.
- feature_027 design-doc examples still show bare `chunk_0.txt` (docs reconciliation pass pending).

### Next

- Package 6 conversation + recovery (AXR-07, AXR-10, AXR-11).

### Notes / context

- Probe census: 18 failed / 2 passing (axr10, axr11 = Package 6).
- StateBackend requires graph context — positive service tests need the StateGraph harness.

---

## 2026-09-20 (iter 5 — package 4 executed, combo A)

### Done

- Implemented A: AXR-04 (helper import, replacement-at-`current`, stop-on-backup-failure, controller invalidation), AXR-08 (stable per-mode ids + legacy-id adoption + per-mode selection), AXR-09 (atomic start_session rebuild, fail-safe to A).
- Verified: 5/5 pkg-4 probes fail as desired; 9 regression scenarios PASS; affected suite 473 passed.
- Probe census: 13 failed / 7 passing (remaining = axr05 ×5 pkg5 + axr10/11 pkg6).
- Proposal + evidence: `sandbox/consistency_enforcement/round_005_package_04_session_lifecycle.md` §Result.

### In progress / Blocked

- Durable `tests/` regressions for pkg 1–4 (needs tests/ canary approval) — packages not closed until landed.

### Next

- Package 5 RAG file handoff (AXR-05).

### Notes / context

- `GoalTree.nodes` is a dict keyed by goal id — iterate `.values()` in tests.

---

## 2026-09-20 (iter 4 — package 3 executed, combo A)

### Done

- Implemented A: validate-before-publish across `add_rule`/`add_rule_safely`/`load_from_repository` + drift-proof `_compile` (`evaluator.py` + TA thought).
- Verified: 4/4 axr03 probes fail as desired; 6 acceptance regressions PASS; `polic|conflict|proposal|reflect` 91 passed.
- Proposal + evidence: `sandbox/consistency_enforcement/round_004_package_03_policy_acceptance.md` §Result.

### In progress / Blocked

- Durable `tests/` regressions for AXR-03 (needs tests/ canary approval) — Package 3 not closed until landed.

### Next

- Package 4 session lifecycle (AXR-04, AXR-08, AXR-09).

### Notes / context

- Direct `add_rule` shares atomicity but no conflict gate (trusted path; conflicts via `resolve_conflicts`).

---

## 2026-09-20 (iter 3 — package 2 executed, combo A)

### Done

- Implemented A: lazy provider refresh + per-request (llm, provider) binding + explicit rebuild-failure errors (`chat_controller.py`, `main_controller.py` reopen hook + TA thought).
- Verified: axr06 probe now fails at stale-routing assertion (actual `['ollama']`); 4 fake-LLM regressions PASS; `chat|model_registry|models|ai_service` 96 passed (incl. legacy `__new__` error-surfacing guards).
- Proposal + evidence: `sandbox/consistency_enforcement/round_003_package_02_provider_dispatch.md` §Result.

### In progress / Blocked

- Durable `tests/` regressions for AXR-06 (needs tests/ canary approval) — Package 2 not closed until landed.

### Next

- Package 3 policy acceptance (AXR-03).

### Notes / context

- In-flight requests finish on captured provider by design; bare `_format_chat_error()` without capture still reports registry selection.

---

## 2026-09-20 (iter 2 — package 1 executed, combo A)

### Done

- Implemented A1+B1+C1: exclusive-temp edit, resolve+validate search + preview cap, canonical deletion guard + canonical-path removal (`coding_tools.py`, `utils.py` + TA thoughts).
- Verified: 3/3 observation probes now fail (fault fixed); inline regressions PASS (AXR-01/02/12); existing `coding|utils|deletion|file_search|file_edit` suite 91 passed.
- Proposal + evidence: `sandbox/consistency_enforcement/round_002_package_01_filesystem_containment.md` §Result.

### In progress / Blocked

- Durable `tests/` regressions for AXR-01/02/12 (needs tests/ canary approval) — Package 1 not closed until landed.

### Next

- Land regression tests (canary), then Package 2 provider dispatch (AXR-06).

### Notes / context

- User said "do all" → interpreted as all of Package 1 (A), not all 6 packages. Packages 2–6 untouched.

---

## 2026-09-20 (iter 1 — v1.0 declared from round_001 analysis)

### Done

- Declared `PROJECT.md` v1.0: scope = 12 round_001 groups (6 P1 + 6 P2), 6-package repair order, per-finding Regression checks as acceptance, probes-retired (not CI), suite-green + ReAct-collection-restored gate.
- Validity re-check: 20/20 observation probes pass on HEAD `52795dd` (= defects reproduced); `git diff fdabeee..HEAD -- src/agentx/` empty — review applies verbatim.

### In progress / Blocked

- _(nothing — awaiting package 1 kickoff)_

### Next

- Scaffold package-1 fix feature: `uv run scripts/omt/new_feature.py "filesystem containment" --type bug_fix --project agentx_1_0_0`, then declare its phase.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- v1.0 declared from round_001 analysis (12 groups, 6 packages); validity re-check 20/20 on HEAD 52795dd

---

## 2026-09-20 (iter 0 — project created)

### Done

- Project home created (`project.py new`, state: draft).

### In progress / Blocked

- _(nothing)_

### Next

- <!-- the single next action -->

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.

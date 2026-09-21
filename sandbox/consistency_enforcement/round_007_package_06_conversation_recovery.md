# Round 007 — Package 6: Conversation persistence + agent recovery (AXR-07, AXR-10, AXR-11)

> Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (override — no OMT gates; `omt_think` + mocked tests + approval gate apply).
> Project: `agentx_1_0_0` (draft) — repair-only, order 1→6, acceptance = per-finding Regression check.
> Scope source: `round_001_implementation_review.md` §AXR-07 / §AXR-10 / §AXR-11 + probes `test_axr06_axr07_console_provider_and_persistence` (AXR-07 assertions), `test_axr10_pending_terminal_update_promotes_second_active`, `test_axr11_validation_exception_leaves_agent_busy`.
> **Approval record:** user approved the recommended combo **A (AXR-07) + B (AXR-10) + B (AXR-11)** (2026-09-20) — proposal above, execution below; this doc records both per strategy steps 3/5/6.

## 1. Confirmed gaps (verified on current tree 2026-09-20, parallel sub-agent analysis)

### AXR-07 — console chat never persists (unfixed; also: no system prompt on this path)

- Console chain `AIChat.run` → `show_chat` → `_chat_view.show()` → `process_user_message`: **no step calls `start_new_conversation`**; `current_conversation_id` stays `None` (`chat_controller.py:17`), so the persistence block (`chat_controller.py:172-174`) never runs → zero rows in `~/.agentx/chat_history.db`.
- `ChatController.show()` (the only system-prompt initializer, via `start_interactive_streaming`, `:123-125`) is **not on the console path** → console model context has **no SystemMessage at all** (probe asserts `len(history) == 2`).
- `start_new_conversation` / `set_current_conversation_id` have zero production callers.
- Reopen hook from pkg 2 (`main_controller.py:114-118`) refreshes provider only — conversation retention will come free from controller caching once the ID is set; the fix must NOT reset history on reopen (D5).

### AXR-10 — pending-goal terminal update violates single-active invariant (unfixed; probe passes)

- `manager.py:87-89`: any transition to COMPLETED/FAILED/ABANDONED calls `_promote_next` unconditionally — no check that the changed goal **was active** nor that no active remains. Terminating a PENDING goal → 2 active goals (`A` + `C`); repeated terminal updates promote more.
- Same-branch collateral (source-inspected): explicit `update_status(..., ACTIVE)` (`:83`) and pre-ACTIVE insertion (`add_goal:45-55` computes actives **after** insert) can create a second active; `revert_adjustment` raw-restores `old_status` (`:169`) without invariant check; `load_from_repository` restores historical double-ACTIVE rows verbatim — **corruption survives restart** (persisted via `INSERT OR REPLACE`, `schema_db.py:176-181`).
- `GoalConfig.max_active_goals` (default 10) is enforcement-dead; `active_goal()`/`act()` consumers are singular (first-active-found completion).

### AXR-11 — validator exceptions escape safe execution; agent stranded busy (unfixed; probe passes)

- `registry.py:155` calls `actuator.validate(command)` **before** the `try` (`:161`) → raising validator escapes `execute_safely` entirely.
- `filesystem_tool.py:82-85` checks `path` truthiness then uses it in `Path / path` without a type check → `path=123` → `TypeError`.
- `agent.py run_cycle` (`:315-349`) and `act` (`:537-566`, sets `ACTING` at `:541` before execute) have **no recovery**: exception → state stays ACTING/DECIDING/REFLECTING → `send_message` gate (`agent_controller.py:193`, `state != PERCEIVING → False`) permanently rejects messages. Exceptions outside tool execution (decide's sqlite path, reflect's `_refl_repo.save` at `:340`) strand the same way.
- No code path in src ever sets PAUSED/TERMINATED (grep-verified) — the fix must preserve such intentional transitions without a blanket `finally` overwrite.

## 2. Fix alternatives

### AXR-07 — persisted console conversations

- **A (recommended)** — lazy lifecycle in `ChatController.process_user_message` (`chat_controller.py` only):
  1. idempotent system-prompt guard at top (insert `SystemMessage` at index 0 iff none present);
  2. lazy persistence block: if `current_conversation_id is None` → create via `history_repo.create_conversation(...)` (raw call, **NOT** `start_new_conversation` — its `start_interactive_streaming` wipes history) then `_save_messages(...)`.
  - First *completed* round creates + stores; failed rounds store nothing; `chat`-and-quit creates no junk row; self-heals after `delete_current_conversation`; zero contact with the pkg-2 reopen branch (D5 preserved by construction). Satisfies all 6 acceptance points (one ID across reopen via controller cache, preserved history, one system prompt, one stored copy per round, repository reconstruction, no new-conversation-on-reopen).
- **B** — `start_new_conversation()` at first entry in `MainController.show_chat` first-open branch. Rejected risks: empty-conversation rows on every quit-without-message; unguarded `AIService()` call can crash entry; lifecycle trapped in wiring the review already called insufficient; silent non-persistence after `delete_current_conversation` until re-wiring.
- **C** — A + centralized `ensure_conversation()` called from `process_user_message`/`show()`/`show_chat` + guarded reopen-continuity + durable entry-path tests. Widest diff; touches freshly-stabilized pkg-2 reopen branch (re-proof burden); best long-term ownership.

### AXR-10 — single-active-goal invariant

- **A** — five scattered micro-guards (`update_status`, `_promote_next`, `add_goal`, `revert_adjustment`, `load_from_repository`). No choke point; load normalization memory-only (poisoned rows re-corrupt every load).
- **B (recommended)** — centralized `_enforce_single_active()` choke point in `GoalManager` (one file):
  1. `update_status`: capture `was_active`; promote only when terminal AND `was_active` AND no active remains (idempotent repeats: goal no longer active → no promote); transition-to-ACTIVE = focus switch (requested goal wins, previous active demoted to PENDING, not lost);
  2. `add_goal`: pre-ACTIVE inserts routed through enforcement;
  3. `_promote_next`: keep H1 priority selection; no-op when an active exists (defense-in-depth);
  4. `revert_adjustment`: enforce after raw restore;
  5. `load_from_repository`: enforce **and persist** — heals historical double-ACTIVE rows so restart converges instead of re-corrupting.
  - `max_active_goals` kept (removal out of scope) but documented as reserved cap; enforcing 1 (NOT 10 — a multi-active tree with singular `active_goal()`/first-found completion is the half-working scheduler the review rules out).
- **C** — B + config realignment (`GoalConfig.max_active_goals` default 10→1 + docstring), `IGoalManager` postcondition docs, `active_goal()` tripwire, repository-level normalization, data-dictionary reconciliation (`analysis_006_data_dictionary.md:103` disagrees with spec §1.3). Code identical to B; extra surface = docs/tests churn.

### AXR-11 — safe-execution boundary + cycle recovery

- **A** — move `validate()` inside the registry `try` (+ one-line filesystem `path` type check). Fails the acceptance bullet "exception elsewhere in the cycle": decide/reflect sqlite errors still strand busy.
- **B (recommended)** — A plus conditional cycle-level recovery:
  1. `registry.execute_safely`: validate inside the exception boundary; validator exception → unsuccessful `ActuatorResult` with actionable error (+ `_log.warning` so validator bugs stay visible);
  2. `filesystem_tool.validate`: type-check `path` → `ValidationResult(valid=False, errors=["'path' must be a string or Path, got int"])`;
  3. `Agent.run_cycle`: wrap body in `try/finally` that restores `PERCEIVING` **unless** state is `PAUSED`/`TERMINATED` (preserves intentional transitions; no blanket overwrite), re-raising so genuine errors stay visible. Precedent: `resume_session`/`start_session` already follow this recovery discipline.
  - Covers all four acceptance bullets: validator-raises → unsuccessful result + busy released; wrong-type → actionable error; exception elsewhere in cycle → released; intentional PAUSED/TERMINATED → preserved; next valid action executes after fixing the rule.
- **C** — B + adjacent hardening: type-validate all built-in validators (rag_sensor/session tools), guard `_refl_repo.save` (degrade to in-memory-only reflection), guard `persist()` (`PERSISTING` also strands), follow-up note for unimplemented `ActionType.PAUSE`→`PAUSED`. Widest surface; alters persistence failure semantics on paths the probe doesn't cover.

## 3. Recommendation

**A (AXR-07) + B (AXR-10) + B (AXR-11)** — each is the smallest change that satisfies its finding's full Regression check, with centralized enforcement where the review explicitly asks for it (AXR-10) and cycle-level recovery where the acceptance demands it (AXR-11). All three leave the pkg-1..5 surfaces untouched. Blast-radius verified: no existing `tests/` pin the buggy behaviors; only the two still-passing observation probes (axr10, axr11) and the AXR-07 assertions flip to failing — the desired post-repair signal (D4: retire/update probes, never gate).

# Result (executed 2026-09-20 — recommended combo A+B+B)

- **Source changes (5 files):**
  - AXR-07 (`chat_controller.py`): idempotent system-prompt guard in `process_user_message` + lazy conversation creation at first completed round via raw `history_repo.create_conversation(...)` (provider attribution from the request-captured `_llm_provider_name`, AXR-06 identity). `start_new_conversation` deliberately NOT reused (its `start_interactive_streaming` clears history). Reopen path untouched (D5).
  - AXR-10 (`manager.py`): `_enforce_single_active()` choke point + `was_active`-gated promotion in `update_status` (focus-switch on explicit activation), pre-ACTIVE insertion demotion in `add_goal`, vacancy no-op guard in `_promote_next`, enforcement in `revert_adjustment` and `load_from_repository` (heals + persists historical double-ACTIVE rows). `max_active_goals` kept as a documented reserved cap (not enforced as concurrency).
  - AXR-11 (`registry.py`, `filesystem_tool.py`, `agent.py`): `validate()` moved inside the `execute_safely` try (+ `_log.warning` so validator bugs stay visible); filesystem `path` type check (`'path' must be a string or Path, got int`); `run_cycle` conditional `finally` restores PERCEIVING unless state is PAUSED/TERMINATED (still re-raises).
- **Observation probes (must stop passing):** all 20 now **fail** — census flipped from 18 failed / 2 passing to **20 failed / 0 passing** (`test_axr10_pending_terminal_update_promotes_second_active` and `test_axr11_validation_exception_leaves_agent_busy` flipped; the AXR-07 assertions in the shared `test_axr06_axr07_console_provider_and_persistence` would also fail — the module already fails at the AXR-06 assertion).
- **Regression proof (16 scenarios, `/tmp/opencode/pkg6_regression.py`, hermetic/mocked):** AXR-07 — console round persists (one ID, one system prompt, one stored copy per round) + reopen retention + reconstructed repository retrieves both rounds; chat-and-quit/failed rounds store nothing. AXR-10 — pending-terminal (COMPLETED/FAILED/ABANDONED) ×3 leaves sole active; repeat-terminal idempotency; exactly-one highest-priority promotion with two candidates inserted opposite to priority; ACTIVE-insertion demotion; explicit-activation focus switch; revert (incl. interim focus switch) restores single active; repository double-ACTIVE-row healing converges across loads. AXR-11 — raising validator → unsuccessful result; wrong path type → actionable error; malformed policy → no strand (`send_message` True, PERCEIVING, next send works); corrected rule executes (act spy); decide-exception releases busy (one-shot, re-raised); PAUSED + TERMINATED preserved. **16 passed, 0 failed.**
- **Existing suites:** `tests/` full run **1908 passed, 0 failed** (+2 deselected = pre-existing `opencode_live` marker default in pyproject, unrelated); feature_007+015 **196 passed**; feature_024 **71 passed**; `tests/controllers` **15 passed**.
- **Residuals:**
  - **Durable `tests/` regressions: LANDED (canary) — Package 6 closed.** 16 scenarios live in `tests/features/feature_024.no_tui_full_features/test_axr07_chat_persistence.py` (2), `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr10_single_active_goal.py` (7), `tests/features/feature_007.agentx_intelligent_agent_behaviour/test_axr11_safe_execution_recovery.py` (7); full suite 1924 passed (1908 + 16). Pkgs 1–5 regressions still pending (their proof was inline-only).
  - AXR-11 out-of-package follow-up (approved alternative excluded it): an exception elsewhere in the cycle still re-raises through `AgentController.send_message`, killing the console REPL loop (`agent_view.py` calls unguarded) — the busy state IS released, so a later turn is never blocked, but the loop dies. Catch-and-surface at the controller is a separate, product-visible decision.
  - No src path sets PAUSED/TERMINATED today (grep-verified) — preservation is future-proofing at zero cost.
  - System prompt still not persisted (consistent with `_save_messages`/`load_conversation` conventions); conversation created at round *completion*, not message *acceptance* (failed first rounds leave no row — cleanest reading of "each completed message stored exactly once").
  - C-extras deferred: `max_active_goals` default untouched (10), data-dictionary vs op-spec §1.3 reconciliation, `IGoalManager` postcondition docs, centralized `ensure_conversation`, guards on `_refl_repo.save`/`persist()`, all-builtin-validator type checks.
  - **ReAct collection restoration (release-gate item, separate from this package):** `tests/conftest.py` still carries the stale blanket exclusion; it hides the *passing* `feature_018` react tests (16/16 green verified outside the excluded path) plus 2 stale-API modules importing never-existing `ReActController`/`ReActView` (collection errors if unhidden). Removing the exclusion + resolving the 2 stale modules needs a tests/ canary and a delete-vs-rewrite decision — asked as follow-up.
- **Next:** release-gate closure — durable regressions canary (pkgs 1–6), ReAct restoration decision, docs pass (feature_027 `chunk_0.txt` examples + design-example reconciliation).

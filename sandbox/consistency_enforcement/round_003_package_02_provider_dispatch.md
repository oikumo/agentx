# Round 003 — Package 2: provider dispatch (AXR-06)

> Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (override — no OMT gates for this run; `omt_think` + mocked tests + approval gate still apply).
> Project: `agentx_1_0_0` (draft) — repair-only, order 1→6, acceptance = per-finding Regression check.
> Scope source: `sandbox/consistency_enforcement/round_001_implementation_review.md` §AXR-06 + probe `test_axr06_axr07_console_provider_and_persistence` (asserts faulty: next message reaches stale `openrouter`, error mislabeled `Ollama`).
> Step: strategy 3 (propose) — STOP at step 4 approval gate. No `src/` edits applied in this round.

## 1. Confirmed gap (summary)

- `ChatController.__init__` (`chat_controller.py:16`) builds `self.llm` once via `AIService().get_current_llm()`; never refreshes.
- `ModelsController.select_provider` updates the shared registry only — no controller refresh.
- `MainController.show_chat` (`main_controller.py:93-105`) returns early when `_chat_controller` exists (reuse, no refresh) — correct for history (D5: no reset on reopen) but stale LLM rides along.
- `_format_chat_error` consults the **registry** current provider, not the llm actually used → after switching to Ollama, a stale-OpenRouter failure is labeled "Ollama".
- Regression check (acceptance): open chat on A → select B → reopen existing chat → next request reaches **only B**; repeat without reopen; B-construction failure → explicit failure, **no silent fallback** to A; errors name the provider used/attempted for that request; refresh preserves conversation ID + history (AXR-07 link).

## 2. Alternatives (pick one)

- **A* — per-request binding + lazy refresh (recommended, report recipe).** `ChatController` tracks `_llm_provider_id`; at the top of `process_user_message` compares with registry current and rebuilds when different (history + `current_conversation_id` untouched). Each request captures `(llm, provider_id/info)` and uses the capture for streaming + `_format_chat_error` (error names used/attempted provider, never registry-new). In-flight request may finish on captured provider; the **next** request honors the new selection. Rebuild failure → fail that request explicitly (no silent use of old LLM). `show_chat` reopen path calls the same refresh (no history reset, D5). Audit note on ReAct/coding/RAG cached lifecycles recorded as residual, not reworked here.
- **B — eager refresh on select.** `select_provider` (or a registry observer) pushes refresh into the live `ChatController` immediately. Fixes the UI-driven path but misses direct registry changes; still needs A's lazy guard + error-binding to be correct. Weaker alone.
- **C — attribution-only (partial).** Fix `_format_chat_error` to use the captured llm identity; leave stale routing. Error honest, prompts still go to old provider. Label partial.
- **D — recreate controller per open (rejected).** Fresh `ChatController` on every `show_chat` picks up B but wipes/risks history and breaks the AXR-07 single-conversation invariant (D5). Listed only to reject.

### Cross-cutting (any pick)
- Preserve conversation ID + history across refresh (shared `ChatController` ownership, D5).
- Mocked tests: fake-LLM registry like the probe; cases: switch+reopen → only B; switch without reopen → only B; B-construction raises → explicit error, zero calls to A; error text names attempted provider; history/ID preserved.
- Probe retired, not gated (D4). Reconcile models/chat design examples with corrected behaviour.

## 3. Approval gate (step 4 — awaiting user)

Reply with a single letter (A/B/C; D is documented-reject). No `src/` edits until go-ahead (step 5). Results go to `# Result` below after execution (step 6).

## 4. Execution notes (for step 5, after approval)

- Mocked unit tests first (rule 3); `omt_think` in touched source (rule 2).
- Record: repaired revision, test nodes/commands, coverage, residuals (in-flight-on-old capture, ReAct/coding/RAG audit).

# Result (executed 2026-09-20 — user picked A)

- **Chosen:** A (per-request binding + lazy refresh). `ChatController`: `_llm_provider_id/name` snapshot + `_init_llm` (failure captured, not raised) + `_ensure_llm_current` (rebuild on selection change, history/ID untouched; rebuild failure → `llm=None` + error so the request fails explicitly naming the attempted provider) + per-request `(llm, provider)` capture in `process_user_message` + `_format_chat_error(exc, provider_id, provider_name)` override (bare calls still fall back to registry). `MainController.show_chat`: best-effort `refresh_provider()` on reopen (no history reset, D5). Legacy `__new__`-constructed controllers adopt pinned llm (older error-surfacing tests keep passing). `omt_think` added.
- **Observation probe (must stop passing):** `test_axr06_axr07_console_provider_and_persistence` → **FAILED as desired** at `assert calls == ["openrouter"]`: actual `['ollama']` (next request now reaches selected provider).
- **Regression proof (this session, fake LLMs):** switch+reopen → only B PASS (same controller, history kept); switch without reopen → only B PASS; B-construction failure → explicit Ollama error, zero A calls PASS; streaming error on captured OpenRouter after registry moved → names OpenRouter, not Ollama PASS.
- **Existing suites:** `test_chat_error_surfacing.py` 4 passed; broader `chat|model_registry|models|ai_service` **96 passed** (incl. legacy `__new__` guards).
- **Residuals:** in-flight request finishes on captured (old) provider by design — only NEXT re-binds; ReAct/coding/RAG cached lifecycles audited-not-reworked (report's audit note); bare `_format_chat_error()` without capture still reports registry selection.
- **Next:** Package 3 policy acceptance (AXR-03). Do not close Package 2 until durable `tests/` regressions land (canary approval needed). CLOSED 2026-09-20: 4 durable tests landed in `tests/features/feature_024.no_tui_full_features/test_axr06_provider_dispatch.py` (canary).

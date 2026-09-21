# Round 006 — Package 5: RAG file handoff (AXR-05, D6: retrieve→offload→delegate kept)

> Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (override — no OMT gates; `omt_think` + mocked tests + approval gate apply).
> Project: `agentx_1_0_0` (draft) — repair-only, order 1→6, acceptance = per-finding Regression check.
> Scope source: `round_001_implementation_review.md` §AXR-05 + 5 probes (service-tool-omits-backend, failed-upload-counted, factory/upload-exceptions-escape ×2, real-graph-path-normalization-and-overwrite).
> **Approval record:** user directive "do it all" (2026-09-20) approved the recommended repair (D6 keep-delegate binding) — proposal + execution in one pass; this doc records both per strategy steps 3/5/6.

## 1. Confirmed gaps (summary)

- `build_rag_v2_tools` bound the path but NOT the backend → service tools never offloaded (`chunks_uploaded=0`); service built a backend for the graph and never connected it to the tools.
- Upload counting ignored per-response `error` → failures counted as successes.
- Relative `chunk_0.txt` keys unreadable through the deepagents filesystem middleware (`validate_path` → `/chunk_0.txt` ≠ stored key).
- Every search restarted filenames at `chunk_0.txt` → sequential/parallel overwrite.
- `build_retriever` + `backend.upload_files` outside the error boundary → exceptions escape the bound public tool.
- `RagSearchHit` had no backend-path field; result schema, analyst prompt, and citations disagreed.

## 2. Repair (as executed — user-approved)

- `_search_documents_impl`: unique `search_id` per invocation; uploads to **absolute** `/retrieval/<search_id>/chunk_<i>.txt` (middleware passes unchanged; collisions impossible); construction/call/upload exceptions → structured `error` (never raise); per-file failures → `upload_errors` (NOT counted in `chunks_uploaded`); `error=None` + empty hits = successful empty retrieval (distinct from offload failure); hits keep content on upload failure (direct answers possible).
- `RagSearchHit.backend_path` + `SearchDocumentsResult.search_id/upload_errors` (schema agreement); `build_rag_v2_tools(path, backend=None)` binds the backend; `RagV2AgentService` constructs the backend BEFORE default tools and passes it (same StateBackend runtime the analyst reads).
- Prompt agreement: orchestrator system prompt + `CHUNK_ANALYST` description/system_prompt name the returned `backend_path` values; "never invent file names".

# Result (executed 2026-09-20 — "do it all")

- **Observation probes (must stop passing):** all 5 axr05 probes **fail as desired** (service tool uploads via backend; failed upload not counted; factory + upload exceptions structured; real-graph reads absolute `/retrieval/...` keys).
- **Regression proof (8 scenarios, real StateBackend graphs where required):** analyst reads every returned path through `validate_path` + `backend.read` PASS; sequential searches never overwrite (first chunk readable + unchanged after second) PASS; parallel same-turn searches never overwrite PASS; failed upload → `chunks_uploaded=0` + `upload_errors` reported PASS; partial upload → 1 success + 1 failure reported PASS; empty retrieval distinct from offload failure PASS; factory + upload exceptions structured (bound tool too) PASS; service-created tool wired to the service backend, analyst-readable inside a graph PASS.
- **Existing suites:** reconciled `test_rag_v2_retrieval_tool.py` (report-directed path-contract update; tests canary logged) + `rag|retrieval|chunk|backend|subagent` **135 passed, 0 failed**.
- **Probe census after pkg 1–5:** 18 failed (fixed findings) / 2 passing (axr10, axr11 — Package 6).
- **Residuals:** legacy non-list `upload_files` returns treated as all-success (tolerance kept); graph-context requirement means service-level positive test needs the graph harness (StateBackend cannot read outside one); design-doc example reconciliation (feature_027 design pages still show `chunk_0.txt`) noted for the docs pass; conversation-reset scratch-discard unverified (report permits reset discarding state).
- **Next:** Package 6 conversation + recovery (AXR-07, AXR-10, AXR-11). Do not close Package 5 until durable `tests/` regressions land (canary approval needed). CLOSED 2026-09-20: 8 durable tests landed in `tests/features/feature_027.rag_v2/test_axr05_rag_file_handoff.py` (canary).

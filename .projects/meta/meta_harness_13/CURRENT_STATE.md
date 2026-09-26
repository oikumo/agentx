# CURRENT_STATE: meta_harness_13

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-26 (iter 0 — project created; inspection and experiments scoped)

### Done

- Created the project mechanically with `uv run scripts/omt/project.py new "Meta Harness 13 — Real OpenCode Session Analysis (Tier 2)" --slug meta_harness_13`; lifecycle state is draft and the generated manifest/WORK project row exist.
- Filled `PROJECT.md` with the canonical proposal for a powerful real-session inspector and labeled experimental workflow, targeting a registered Tier-2 `omt_session` tool.
- Incorporated both user refinements: deep inspection is essential; labeled messages for running experiments are an equally important core feature.
- Defined session trees, full message/part/tool/reasoning drill-down, typed cross-session queries, traces, usage reconciliation, failure diagnosis, live snapshots, comparison, and reproducible exports.
- Defined the proposed message-label protocol and experiment lifecycle: manifest → dry run → explicitly invoked independent trials → capture/validate → quality-aware comparison/replay. Included runs/cases/variants/repetitions/attempts, nested spans, child bindings, contamination checks, and independent sample accounting.
- Reviewed Harness Reason features 129/130 and closure: reuse their capture contracts and explicit unknowns; preserve the negative general-engine promotion result. Legacy labels remain importable without treating repeated ledger replays as independent trials.
- Inspected current toolbox discovery (`list --tier 2`, `query session`): no real-session inspector is registered. Baseline compiler check: 275 records / 0 errors; `tool_args` headroom is 39 bytes and needs a deliberate integration budget plan.
- Declared the project-creation task as `docs`/Analysis, consulted thoughts for both new files (none), and verified project-document edit preflight is clear.
- Validation: `project.py sync` and `project.py status meta_harness_13` confirm the draft; `harnessc.py check` passes (275 records, 0 errors; existing 39-byte tool-argument headroom warning); both project documents have no unresolved template placeholders and all 9 relative Markdown links resolve; `git diff --check` passes.
- `omt_complete` verified the docs/Analysis artifacts. Repository regression: `env PYTHON_DOTENV_DISABLED=1 LLAMA_CPP_MODELS_CACHE_PATH=/tmp uv run pytest -q` → **2006 passed, 2 deselected, 7 deprecation warnings** in 91.52 seconds. Restored the six generated toolbox files changed by the test run to their clean pre-test state; retained the project documents and mechanically synced manifest/WORK row.

### In progress / Blocked

- Project creation/proposal only. No feature ID allocated, implementation begun, real session content harvested, trial launched, or runtime/tool registry changed.
- Option A (dedicated Tier-2 inspector and labeled experiments) is recommended; implementation approval is pending under the project workflow's step 6.
- Project creation and validation are complete. Runtime implementation remains the next, separately approved project step.

### Next

- Review `PROJECT.md` §Implementation plan for approval. Once approved, use `new_feature.py` to allocate/link `opencode_session_inspection_and_experiments` as a `major_feature`, then begin M1 contract/schema verification with a design document and the required TDD process.

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
- Treat Tier 2 as full harness registration/build/budget/e2e integration, not merely the toolbox tier filter. A read-only query and an experiment run have different enforcement requirements.
- Do not mark the project complete or reopen `harness_reason` as a side effect. The draft's core scope includes both inspection and experiments; neither may be dropped silently.

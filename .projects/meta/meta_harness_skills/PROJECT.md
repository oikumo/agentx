# PROJECT: meta_harness_skills — Meta_Harness_Skills

> Status: **active** · **v0.3 (2026-10-12)** — scope locked to ALL (A+B+C+D = full rollout). Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project meta_harness_skills`; log sessions in CURRENT_STATE.md (newest on top).
> Source idea: `.sandbox/ideas/meta_harness_skills/meta_harness_skills_review_analisys.md` (604 lines, ES) + companion `meta_harness_skills_review_2026-10-11.md` (proposal, 2026-10-11, SHA fef76600c3bb9447b3afb79b11c0dd8c0b5f9112).

---

## New Session Quick Start

> Procedural OpenCode skills layer over META HARNESS — not a product runtime.

**Next:** pick an alternative (A/B/C/D in session 2026-10-12 entry) → approve plan → spawn first feature.

---

## Summary (one line)

Small procedural `SKILL.md` layer over existing OMT tools/gates/state to cut mistaken steps — starting with block-recovery + work-resumption, contracts before autonomy.

---

## Purpose

### What this project is

- Implement the 6-skill proposal as **procedural, stateless-by-default** OpenCode skills (`SKILL.md` + `skill.contract.json` + refs/scripts) that **reuse** OMT authority (preflight, gates, receipts, TDD, net, ledger, PROJECT/CURRENT_STATE) — never duplicate it.
- Order per analisys §Recomendaciones: **fix CI/repro → formalize minimal contracts (skill + OmtResult envelope + StateScope) → 2 manual-only pilots (`omt-recover-block`, `omt-resume-work`) → fix `omt_session` compat → contract/scenario/replay tests → `omt-verify-closeout` → only then measure autoinvoke/benefit.**
- 8-week rollout starting **2026-10-12** with 5 gates: base-green (10-18) → contract-stable (10-30) → pilot-functional (11-08) → evidence-reliable (11-15) → rollout-decision retain/revise/drop/inconclusive (12-04).

### What this project is **not**

- Not a skill-runtime / RPC (`init/invoke/close`), not a second state store (no `.skill-state.json`), not AgentX product API (no HTTP/FastAPI — REPL `agentx.main:start`, MVC/Partner `perceive→decide→act→reflect`), not a policy copy inside skill text, not auto-applied fixes.

---

## Scope & success criteria

**In scope (from analisys):**
1. `skill.contract.json` v1 + validator (`trigger, near-misses, requires, allowed/forbidden_effects, state_owner=external, result_schema=omt-skill-result/v1, stop_when`) + `skill doctor/scaffolder` (`skill.py doctor|new|test|list`).
2. `OmtResult<T>` envelope v1 (`ok` true only on objective success; `outcome succeeded|blocked|not_applicable|inconclusive|failed`; `code` machine-readable e.g. RECEIPT_REQUIRED/TDD_RED_REQUIRED; `blocker{gate,code,message,remediation,requiresApproval}`; `evidence[]`; `retryable`; `stateRevision`) + adapters.
3. `StateScope` ownership doc (invocation/session/feature/project/harness — skills NOT a scope).
4. Pilots manual-only (`opencode/autoinvoke:false`): `omt-recover-block`, `omt-resume-work`, then `omt-verify-closeout`; deferred: `omt-deliver-change`, `omt-session-evidence` (blocked on `schema_unsupported`), `omt-evaluate-skill` (mature phase).
5. Test pyramid before 24-trial live pilot (4 cases × baseline/treatment × 3 reps): schema/lint → contract → scenario/golden → witness-replay → integration (fake OMT) → live-smoke → experiment (quality first, tokens/time/retries second).
6. Base fixes: `uv sync --frozen` vs missing `uv.lock` (+`.gitignore` has `uv.lock`), pytest-critical in PR (not nightly-only `split.yml`), dep/security audit, `load_dotenv(override=True)` → `False` + `AGENTX_DOTENV_OVERRIDE=1` opt-in, action-SHA pinning (optional strict), test-count drift autogen.

**Success criteria:**
- Checkout-clean `uv sync --frozen` green; critical pytest in PR.
- No textual heuristic needed to tell blocked vs succeeded (envelope).
- Pilots pass positive/negative/bypass witnesses; resume reconciles without inventing state.
- `omt_session` reads live DB read-only or returns versioned machine-readable error (no secret skill-side SQLite path).
- Autoinvoke decision only on pre-declared near-miss-rate + outcome-quality thresholds.

**Out of scope:** AgentX runtime changes beyond dotenv/config hardening; second harness; LLM-e2e before deterministic greens.

---

## Status

- [ ] First linked feature (header flips draft → active mechanically)
- [x] Home created 2026-10-11/12, PROJECT.md v0.2 distilled from analisys
- [ ] Awaiting user pick on alternatives (see CURRENT_STATE 2026-10-12)

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — Procedural skills, external authority:** `SKILL.md` = discover→authorize-load→load→execute-via-OMT→result→unload; OMT/tool gate decides effects (skill `allow` ≠ tool `allow`). Rationale: OpenCode model + analisys §Permisos + OpenAI-MCP least-privilege analogue.
- **D2 — Contracts before autonomy:** envelope + contract + StateScope precede any autoinvoke. Rationale: transport-success vs semantic-block confusion + schema_unsupported cannot be prompt-fixed.
- **D3 — Small-first:** recover-block + resume-work manual-only before deliver-change/evaluate. Rationale: LangGraph small-node retry + MAF agent-vs-workflow + CrewAI crews-vs-flows — deterministic harness decides, skill routes.
- **D4 — No skill state:** skills stateless; memory lives in session/feature/project/harness owners. Rationale: LangGraph checkpointer-vs-store split.
- **D5 — Policy by reference, not by copy:** skill queries current OMT response as authority. Rationale: avoids drift; test-count drift precedent.

---

## References

- Idea: `.sandbox/ideas/meta_harness_skills/meta_harness_skills_review_analisys.md`
- Proposal: `.sandbox/ideas/meta_harness_skills/meta_harness_skills_review_2026-10-11.md`
- Vision/DSL: `META_VISION.md`, `.meta/META_HARNESS.omt` (g.net fail-closed L132 vs vision shorthand)
- Catalog: `.workflows/META.md` → `meta_harness/META.md` → `loops/meta_harness_project.md` (this execution)
- Product entry: `agentx.main:start`; domain `IAgentModelPartner`; lifecycle INITIALIZING→…→TERMINATED; `pyproject.toml` (py≥3.14, langgraph==1.2.10, deepagents==0.7.5); `src/agentx/ui/screens/main/main_controller.py`
- CI: `.github/workflows/split.yml`; existing skill example `.agents/skills/`; `.opencode/{lib,plugins}`

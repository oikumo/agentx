# PROJECT: agentx_1_0_0 — AgentX 1.0.0 (consistency hardening release)

> Status: **active** · v1.0 RELEASED (2026-09-20) — definition locked from `sandbox/consistency_enforcement/round_001_implementation_review.md` (12 open groups, verified 2026-09-19 at `fdabeee`, re-verified on HEAD `52795dd`: 20/20 probes pass, `src/agentx/` diff empty). All 12 round_001 groups repaired across packages 1–6 with per-finding regression proof (48 durable tests); 20/20 observation probes retired (D4); full suite green (1972 passed); ReAct collection restored; docs reconciled. Session log in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: **AgentX 1.0.0 ships the current app with all 12 round_001 finding groups (6 P1 + 6 P2) repaired and proven by regression tests — no new features.**

**Next:** pick work package 1 (filesystem containment: AXR-01, AXR-02, plus AXR-12 policy share) and scaffold its fix feature dir, e.g. `uv run scripts/omt/new_feature.py "filesystem containment" --type bug_fix --project agentx_1_0_0`, then declare its phase.

---

## Summary (one line)

**AgentX 1.0.0 is the consistency-hardening release that closes the 12 confirmed round_001 defects (sandbox escapes, policy/session/RAG/provider/chat/agent-recovery flaws) with per-finding regression proof — functionality unchanged, trust restored.**

---

## Purpose

### What this project is

- A **repair-only release** driven by `sandbox/consistency_enforcement/round_001_implementation_review.md` + `round_001_review_probes.py` (20 observation probes, all passing = defects reproduced on current HEAD).
- Closes **6 P1** (AXR-01 coding-edit symlink overwrite, AXR-02 search symlink read, AXR-03 stale policy cache + premature publish, AXR-04 `new` NameError + broken restart, AXR-05 RAG upload wiring + paths + errors, AXR-06 stale provider dispatch) and **6 P2** (AXR-07 chat persistence, AXR-08 PID-derived IDs, AXR-09 `start_session` stale storage, AXR-10 multi-active goals, AXR-11 validator escape + stuck busy, AXR-12 deletion-guard traversal).
- Executes the report's **6-package repair sequence** (§Repair sequence) with each finding's stated **Regression check** as its acceptance contract.

### What this project is **not**

- **Not new functionality.** No new screens, providers, RAG patterns, stores, or DSLs. Novel work belongs to other projects (`rag_v2`, `petri_net_studio`, `workflows`).
- **Not a redesign.** Architecture stays; repairs reconcile code with the existing design/operation-spec contracts cited per finding.
- **Not live-provider / terminal-input / full-conversation proof.** Those remain outside round_001 coverage and stay out of 1.0.0 acceptance (listed as limitations, not silent gaps).
- **Not a probe-greening exercise.** Observation probes asserting faulty behavior must *stop passing* and be *replaced* by regression tests asserting desired behavior — never added to CI as correctness gates.

---

## Scope & success criteria

### In scope (the 6 repair packages, in order)

| # | Package | Findings | Completion boundary |
|---|---|---|---|
| 1 | Filesystem containment | AXR-01, AXR-02 (AXR-12 shares the path policy) | Outside markers unchanged/unreadable via tool paths; ordinary sandbox ops work |
| 2 | Provider dispatch | AXR-06 | Next request uses selected provider or fails explicitly; error attribution matches request |
| 3 | Policy acceptance | AXR-03 | One compile/conflict/persist/publish contract; rejected changes leave accepted behavior intact |
| 4 | Session lifecycle | AXR-04, AXR-08, AXR-09 | Create/rebind/save/reconstruct/resume agree on storage + stable identity; legacy data recoverable |
| 5 | RAG file handoff | AXR-05 | Service retrieval yields uniquely identified backend files readable by the real analyst tool; errors/citations accurate |
| 6 | Conversation + recovery | AXR-07, AXR-10, AXR-11 | Chat round survives reconstruction; single-active-goal invariant holds; failed turn releases busy state |

### Success criteria (all must hold at release)

- Every finding's **Regression check** passes as a real regression test (public behavior, not injected-only paths; parallel-search/analyst-handoff, restart, and failure-injection cases the report names).
- The 20 observation probes **no longer pass** for repaired findings (each replaced, none gated in CI).
- Full suite green (`uv run pytest -q` + explicit ReAct controller module after removing the stale `tests/conftest.py` blanket exclusion).
- Design examples and test assertions reconciled with corrected behavior; each finding records repaired revision, test nodes/commands, coverage, and residual limits; narrower repairs labeled partial.

---

## Status

- [x] Definition declared (v1.0 — scope = round_001's 12 groups + 6-package order + acceptance above)
- [x] Package 1 — filesystem containment (feature dir + phase + fix + regressions)
- [x] Package 2 — provider dispatch
- [x] Package 3 — policy acceptance
- [x] Package 4 — session lifecycle
- [x] Package 5 — RAG file handoff
- [x] Package 6 — conversation + recovery (fix + durable regressions landed; closed)
- [x] Release gate — all regression checks green, probes retired, suite green, ReAct collection restored
- [x] First linked feature (header flips draft → active mechanically)

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — Scope is round_001's 12 groups, nothing else.** 1.0.0 adds no features and takes no adjacent refactors. New defects found mid-release become 1.0.1 candidates, not silent scope.
- **D2 — Repair order is the report's 1→6.** Packages 1–3 unblock trust boundaries first; 4–6 share lifecycle ownership. Independent packages may run in parallel; no finding closes because an adjacent package completed.
- **D3 — Acceptance = each finding's Regression check.** A passing suite or a failing observation probe is a signal, not proof. Close only on stated acceptance; label narrower work partial.
- **D4 — Observation probes stay out of CI.** `round_001_review_probes.py` remains a review artifact under `sandbox/`; run separately with `uv run pytest -q sandbox/consistency_enforcement/round_001_review_probes.py`.
- **D5 — Shared contracts, single owners.** Provider refresh + conversation creation share `ChatController` (no history reset on reopen); AXR-04/08/09 share one session-ownership contract; AXR-01/02/12 share one path policy with an explicit concurrent-rename threat bound.
- **D6 — RAG keeps retrieve→offload→delegate.** Repair binds tools to the service backend with `/retrieval/<search_id>/chunk_N` paths plus schema/prompt/citation agreement — or records an explicit product decision to drop file-based delegation (with prompt/test updates).

---

## References

- `sandbox/consistency_enforcement/round_001_implementation_review.md` — canonical findings, evidence basis, coverage gaps, repair sequence (this project's scope source).
- `sandbox/consistency_enforcement/round_001_review_probes.py` — 20 observation probes (run separately; not CI).
- Validity re-check 2026-09-20: 20/20 pass on HEAD `52795dd`; `git diff fdabeee..HEAD -- src/agentx/` empty.
- Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (Rules line 1: **override** — do not follow OMT methodology, focus on the application as a whole; approval gate + `omt_think` + mocked tests + sandbox proposals still apply).
- Design anchors per finding: feature_019 coding (File Edit / OP-5), feature_007 agent operation spec (§1.1–1.5), feature_027 RAG v2 operation spec + persistence-strategy decision.

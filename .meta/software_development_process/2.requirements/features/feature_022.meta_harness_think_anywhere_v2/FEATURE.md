# Feature 022: Meta Harness Think Anywhere V2

> **Status:** [~] Tier A + Tier B1+D1 + Tier C shipped (2026-07-18); Tiers B2, E pending as separate WORK.md tasks
> **Created:** 2026-07-18
> **WORK.md task:** `feature_022.meta_harness_think_anywhere_v2`
> **Builds on:** feature_021.meta_harness_think_anywhere (`.opencode/plugin/omt_think.ts`, think-gate in `.opencode/plugin/omt_enforcer.ts`)
> **Source theory:** `.meta/doc/harness/think_anywhere_langchain.md`
> **Origin:** post-mortem evaluation of feature_021 against the Think-Anywhere paper (2026-07-18 session).

---

## Summary

feature_021 delivered a working persistent `TA:` thought-tag layer (insert/list/remove + session
digest + blocking think-gate) and is genuinely adopted — real thoughts already exist in
`src/agentx/ui/tui/screens/main_screen.py:77-79`. However, a structured evaluation against its
source theory and its production behaviour found **13 flaws**: 3 correctness-class (one already
hit in the wild), several enforcement-semantics gaps, robustness issues, and — most importantly —
the adaptation kept only the paper's *aesthetic* ("inline, at point of need") while dropping its
two load-bearing mechanics: **entropy-guided placement** and **outcome-validated thinking**
(RLVR). This feature hardens the v1 implementation and closes the intent gap, tiered so the
cheap correctness fixes land first.

## Scope (one sentence — what "done" looks like)

`TA:` insertion is string-context-aware and extension-safe, the think-gate pattern matches only
real comment tags (no prose/substring false positives), thoughts are anchor-addressed (not raw
line numbers), a file's thoughts surface non-blockingly at first read, and a verification
lifecycle (`verified`/`stale`) gives thoughts an RLVR-style feedback signal — all covered by
deterministic tests.

## Task type

`major_feature` (touches the OMT enforcement surface: plugin + enforcer gate + docs)

---

## Evaluation findings (evidence-backed, prioritized)

### 🔴 Correctness

| # | Flaw | Evidence |
|---|------|----------|
| F1 | **String-context-unaware insertion.** `omt_think` inserts by raw line number with no lexical awareness; `# TA:` inside a triple-quoted string breaks the host file. **Already happened in production** (Textual CSS parser break). Same class: Markdown code fences, SQL strings, docstrings. | Self-documented at `src/agentx/ui/tui/screens/main_screen.py:78-79` |
| F2 | **Unsafe default comment syntax.** Unknown extensions default to `#`, which is not a comment in `.go/.rs/.java/.c/.cpp/.sql/.html/.xml` — insertion would break those files. Design doc's "safe for most text formats" is false. | `omt_think.ts:50-51` |
| F3 | **Gate false positives.** Think-gate greps plain substring `TA:`; matches prose *about* TA: and substrings inside `META:`/`DATA:`. Live today: `feature_001…/software_development_consortium.md` matches accidentally; the gate also fires on the harness's own files (`omt_think.ts` ~20 hits, `omt_enforcer.ts`, `AGENTS.md`, `META_HARNESS.md`). Files that *discuss* the marker are gated as if they *carry* thoughts. | `omt_enforcer.ts:232`; grep audit 2026-07-18 |

### 🟡 Enforcement semantics

| # | Flaw | Evidence |
|---|------|----------|
| F4 | **Consult is session-global + cross-session.** One `omt_think_list` clears the gate for *all* files, and `hasConsultedThoughts` accepts *another session's* consult within `UNLOCK_WINDOW_MS` — undercuts the "safety-relevant, not bypassable" claim. | `omt_enforcer.ts:203-225` |
| F5 | **Reactive-only delivery.** Thoughts surface only as an edit *block* (error UX, one step late, once per session). Nothing injects a file's thoughts when the agent first *reads* it — the point closest to generation. | `omt_enforcer.ts:933-943` |

### 🟡 Robustness

| # | Flaw | Evidence |
|---|------|----------|
| F6 | **Fragile anchoring.** Raw line numbers drift on any edit above; JSONL index goes stale immediately; `omt_think_remove` can target the wrong `TA:` line after shifts (only partially mitigated by the contains-check). | `omt_think.ts:195-208, 273-285` |
| F7 | **Sloppy filters.** `category` not lowercased (description promises lowercase → filter mismatch); `query` interpolated unescaped into a grep regex; dead ternary with identical branches. | `omt_think.ts:229-231` |
| F8 | **Write-only index.** Nothing reads `thoughts.jsonl` in v1 (list greps inline) — pure I/O + drift surface for zero current value. | design §4 ("not read by list in v1") |
| F9 | No dedup on add; CRLF files get mixed line endings. | `omt_think.ts:191-206` |

### 🔵 Theory doc defects (`.meta/doc/harness/think_anywhere_langchain.md`)

| # | Flaw |
|---|------|
| F10 | Line 12 formula typo: `P(c \| x, s` — unclosed paren. |
| F11 | `pass_at_k` computes `passed/k`, which is **not** pass@k (unbiased estimator: `1 − C(n−c,k)/C(n,k)`); `build_sampler(k=…)` ignores `k`. |
| F12 | `analyze_thinking_positions` claims to attribute each block to a syntactic context but only histograms AST nodes of the *stripped* code — doc/code mismatch. |
| F13 | Mid-statement block stripping can change semantics (e.g., inside a call's arg list); only syntax is ever validated; no sandbox warning for executing model code. |

### Intent-gap analysis (paper vs feature_021)

| Paper mechanic | feature_021 analogue | Verdict |
|---|---|---|
| Entropy-guided **placement** (Assign > Return > Expr > If) | Agent guesses raw line numbers | ❌ absent |
| **Validation** of thinking (`R = 0.1·R_struct + 0.9·R_correct`) | Nothing — a wrong thought persists forever and the gate forces reading it | ❌ absent |
| Thinking injected **during** generation | Digest at session.start (far from use); gate block at first edit (reactive) | ⚠️ partial |
| Strip-to-execute guarantee | "language-valid comment" — broken by F1 in the wild | ⚠️ broken |

---

## Proposed improvements (tiered; tiers are independently shippable)

### Tier A — Correctness hotfixes (fixes F1–F3, F7, F9) — *do first*
- **A1.** Anchor gate/retrieval pattern to real comment syntax: `^\s*(#|//|/\*|<!--)\s*TA:` — kills META:/DATA:/prose false positives.
- **A2.** Deny unknown extensions; add explicit mappings for `.go/.rs/.java/.c/.cpp/.h/.sql/.html/.xml`.
- **A3.** String-guard: refuse insertion inside triple-quoted strings / code fences (cheap `"""`/`'''`/```` ``` ```` counting heuristic; `tokenize`-based check for `.py`).
- **A4.** Lowercase `category`; regex-escape `query`; remove dead ternary; dedup identical (path, thought).

### Tier B — Restore placement intelligence (fixes F6)
- **B1.** Anchor-based insertion: `omt_think{path, after:"def foo("}` / `symbol:` resolved via grep/AST — drift-resistant; store anchor in index for reconcile.
- **B2.** `omt_think_suggest{path}`: AST-walk ranking candidate sites using the paper's table (Assign > Return > If…) — mechanical high-entropy position targeting.

### Tier C — Restore the feedback loop (fixes F4, intent gap)
- **C1.** `omt_think_verify{path,line}`: re-check a thought against current code → mark `verified`/`stale`; digest reports stale count; gate weights unverified `risk:` thoughts higher.
- **C2.** Per-file consult granularity (consult clears gate only for consulted files); drop cross-session window for `risk:` category.

### Tier D — Point-of-use delivery (fixes F5)
- **D1.** Non-blocking injection on first *read* of a thought-carrying file (before-hook on read tools) — thoughts arrive *before* generation, not as an edit error.

### Tier E — Housekeeping (fixes F8, F10–F13)
- **E1.** Index: consume it (gate lookup, drift repair, analytics) or delete it.
- **E2.** Fix the theory doc: pass@k estimator, formula typo, position-analysis mismatch, sandbox warning, dead streaming stub.

**Recommended sequencing:** Tier A as one bug_fix-style batch → B1 + D1 (biggest intent-gap closers) → C1 → remainder by value.

---

## Use case

### Actor
opencode coding agent (the `build` agent) across sessions / context windows.

### Goal
Trustworthy, precisely-placed, self-maintaining `TA:` thoughts that surface at the point of need
without false-positive gate noise or file-corruption risk.

### Main flow (post-v2)
1. Session starts → digest (anchored pattern; includes stale-thought count).
2. Agent first reads a thought-carrying file → thoughts injected non-blockingly (D1).
3. Agent adds a thought → anchor- or symbol-addressed insertion (B1), string-guarded (A3),
   extension-safe (A2), deduped (A4).
4. Agent edits a thought-carrying file → gate fires only on real comment tags (A1), cleared
   per-file by consult (C2).
5. Agent/harness periodically verifies thoughts → stale ones flagged (C1), removable.

### Guardrails (carried from v1, unchanged)
- Hard-deny on `.env*`, `README.md`, `uv.lock`, `LICENSE`, `.json`; never creates files.
- Think-gate not bypassable by `omt_skip`; token caps: digest 30, list 50.

## Operations extracted (candidate; final set decided in Design)
- `omt_think(path, thought, after?|symbol?|line?, category?)` — string-guarded, extension-safe, deduped (A2–A4, B1)
- `omt_think_list(path?, category?, query?)` — anchored pattern, escaped query, lowercase category (A1, A4)
- `omt_think_remove(path, line|anchor)` — anchor-aware reconcile (B1)
- `omt_think_suggest(path)` — AST-ranked insertion-site suggestions (B2)
- `omt_think_verify(path, line)` — verified/stale lifecycle (C1)
- read-time injection hook (D1); per-file consult ledger records (C2)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_022.meta_harness_think_anywhere_v2/FEATURE.md` | [x] |
| Analysis (Tier A) | Analysis doc | `3.analysis/features/feature_022.meta_harness_think_anywhere_v2/analysis_001_tier_a_hotfixes.md` | [x] |
| Design (Tier A) | Design doc + op spec | `4.design/features/feature_022.meta_harness_think_anywhere_v2/design_001_tier_a_hotfixes.md` | [x] |
| Implementation (Tier A) | Impl notes | `5.implementation/features/feature_022.meta_harness_think_anywhere_v2/implementation_notes.md` | [x] |
| Testing (Tier A) | Test report | `6.testing/features/feature_022.meta_harness_think_anywhere_v2/test_report.md` | [x] |
| Analysis (Tier B1+D1) | Analysis doc | `3.analysis/features/feature_022.meta_harness_think_anywhere_v2/analysis_002_tier_b1_d1.md` | [x] |
| Design (Tier B1+D1) | Design doc + op spec | `4.design/features/feature_022.meta_harness_think_anywhere_v2/design_002_tier_b1_d1.md` (+ `operation_spec_tier_b1_d1.md`) | [x] |
| Implementation (Tier B1+D1) | Impl notes | `5.implementation/features/feature_022.meta_harness_think_anywhere_v2/implementation_notes_tier_b1_d1.md` | [x] |
| Testing (Tier B1+D1) | Test report | `6.testing/features/feature_022.meta_harness_think_anywhere_v2/test_report_tier_b1_d1.md` | [x] |
| Analysis (Tier C) | Analysis doc | `3.analysis/features/feature_022.meta_harness_think_anywhere_v2/analysis_003_tier_c.md` | [x] |
| Design (Tier C) | Design doc + op spec | `4.design/features/feature_022.meta_harness_think_anywhere_v2/design_003_tier_c.md` (+ `operation_spec_tier_c.md`) | [x] |
| Implementation (Tier C) | Impl notes | `5.implementation/features/feature_022.meta_harness_think_anywhere_v2/implementation_notes_tier_c.md` | [x] |
| Testing (Tier C) | Test report | `6.testing/features/feature_022.meta_harness_think_anywhere_v2/test_report_tier_c.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

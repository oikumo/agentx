# Implementation Notes: feature_021.meta_harness_think_anywhere

> **Feature:** Meta Harness Think Anywhere
> **Type:** major_feature
> **Phase:** Implementation
> **Status:** Complete

---

## 1. What was built

A persistent, grep-friendly inline `TA:` thought-tag layer for the META HARNESS, adapting the
Think-Anywhere paper's on-demand reasoning to a cross-session annotation/memory mechanism.

| Surface | Change |
|---|---|
| `.opencode/plugin/omt_think.ts` | NEW standalone plugin: `omt_think` / `omt_think_list` / `omt_think_remove` + `session.start` digest |
| `.opencode/plugin/omt_enforcer.ts` | ADD pure `thinkGateDecision` + `hasConsultedThoughts` + before-hook integration (EDIT_TOOLS only) |
| `opencode.jsonc` | allow the 3 think tools |
| `AGENTS.md` | "Think Anywhere (feature_021)" MANDATORY section |
| `.meta/META_HARNESS.md` | `SECTION:THINK` + `THINK_*` tags |
| `.meta/.omt/thoughts.jsonl` | NEW append-only structured sidecar (gitignored runtime state) |
| `tests/features/feature_021.../` | TDD suite + `_think_runner.mjs` / `_think_gate_runner.mjs` fixtures |

## 2. Contract honored (mirrors feature_020 defect-free plugins)

- `import { tool } from "@opencode-ai/plugin"`; `args` + `tool.schema.*` (DEFECT-C safe)
- `async execute(args, context)` returns plain strings (DEFECT-D safe)
- **only `export default`** — NO named exports (DEFECT-A load-crash safe; see §3)
- file ops via `execFileSync` / `readFileSync` / `writeFileSync` (no shell — H3 safe)

## 3. Defect fixed during implementation (T1)

`omt_think.ts` initially named-exported `commentSyntaxFor` and `fileThoughts`. opencode's loader
calls every named export at load time with a non-string arg, so `commentSyntaxFor(ext)` crashed
with `(ext || "").toLowerCase is not a function` — the plugin never registered in a real session.
Fix: un-exported both (kept only `export default`), matching `omt_nav.ts` / `omt_status.ts`.
Verified via real `opencode serve` (zero `failed to load plugin`). A deterministic structural
guard (`test_no_named_exports_except_default`) now prevents regression. See
`6.testing/.../test_report.md` §3.

## 4. Guardrails

- Hard-deny insert/remove on `.env*`, `README.md`, `uv.lock`, `LICENSE`, `.json`.
- `omt_think` never creates a file that doesn't exist.
- `omt_think` bypasses phase/canary gates (annotation, not functional change) — deliberate.
- Think-gate is NOT bypassable by `omt_skip`; cleared only by `omt_think_list` (active consult).
- Token budget: retrieval O(hits); digest capped at 30; list capped at 50.

## 5. Verification

- 30/30 feature_021 tests pass; 174/174 across feature_020+021+016+scripts/omt.
- MVC++ lint: 0 errors, 33 warnings (baseline; no `src/` business code touched).
- Real `opencode serve` loads `omt_think.ts` cleanly.

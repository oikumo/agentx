# Implementation Notes: feature_022.meta_harness_think_anywhere_v2 — Tier A

> **Feature:** Think Anywhere V2 — Tier A correctness hotfixes (A1–A4)
> **Type:** major_feature | **Phase:** Implementation | **Status:** Complete
> **Design:** `4.design/.../design_001_tier_a_hotfixes.md` | **Scope decision:** Tier A only; B/C/D/E deferred as separate WORK.md tasks

---

## 1. What was built

Correctness hotfixes to the feature_021 think-anywhere layer, per post-mortem flaws F1/F2/F3/F7/F9
(+ A1b noise-dir excludes, dead-code removal). No tool-surface changes (opencode.jsonc, AGENTS.md,
META_HARNESS.md untouched).

| Hotfix | Surface | Change |
|---|---|---|
| A1 anchored pattern | `omt_think.ts`, `omt_enforcer.ts` | `THOUGHT_PATTERN = "^\s*(#|//|/\*|<!--|--)\s*TA:"` const in BOTH files (byte-identical, keep-in-sync comments; plugins are standalone — no cross-imports). `grepThoughts`/`fileThoughtsIn` gained `-E`; `thinkDigest`/`omt_think_list` base pattern = the const; `omt_think_remove` line check uses `new RegExp(THOUGHT_PATTERN)` instead of `includes("TA:")`. `--` (sql) opener included so the gate is never blind to what think emits. |
| A1b excludes | `omt_think.ts` | `grepThoughts` gained `--exclude-dir=.venv --exclude-dir=__pycache__` (digest pollution: 220 hits → true count). |
| A2 extension map | `omt_think.ts` | `commentSyntaxFor` is now an explicit map: hash/slash/html/css-block/sql families (+ `.go .rs .java .c .cpp .h .hpp .cs .swift .kt .scala .html .xml .vue .svelte .scss .less .sql`). Unknown/extensionless → `null` (deny). Unsafe `#` default + its false comment deleted. Refusal message points at `commentSyntaxFor`. |
| A3 string guard | `omt_think.ts` | `inStringContext(lines, insertAt, ext)`: naïve delimiter parity over lines BEFORE the insertion point — `"""`/`'''` for `.py`, ``` ``` ```/`~~~` fences for `.md`/`.mdx`; other exts pass. Called after clamping, before `splice`; refusal message cites the F1 (Textual CSS) incident. Failure direction = refuse (safe). |
| A4 filters/dedup/EOL | `omt_think.ts` | `escapeRegex` applied to `query` + category (dead ternary deleted); category lowercased at insert (`buildThoughtLine`) and at filter (`omt_think_list`); dedup: normalized `(cat, text)` pair comparison via `parseThoughtLine`, refusal points at existing line; EOL: `split(/\r?\n/)` + `join(eol)` where `eol` follows the file (CRLF files stay CRLF, LF byte-identical to v1). |
| dead code | `omt_think.ts` | `fileThoughts` deleted (unused; third copy of the F3 substring bug). |

## 2. Contracts preserved (feature_020/021 regression surface)

- Only `export default` leaves `omt_think.ts` (DEFECT-A; `THOUGHT_PATTERN` is a module const, NOT exported).
- `tool` + `args`/`tool.schema.*` (DEFECT-C); plain-string results (DEFECT-D); `execFileSync` argv (H3).
- Enforcer keeps named function exports (`thinkGateDecision`, `hasConsultedThoughts`, `fileThoughtsIn`)
  — that file's loader contract differs (enforcer is wired, not tool-registered).
- v1 behaviors unchanged: protected denylist evaluated first; `.json` dedicated refusal; never creates
  files; success message format `✅ TA: <text> → <rel>:<n>`; list cap 50 / digest cap 30; consult
  recorded even on empty results; remove round-trips CRLF (`split("\n")` preserves `\r`).

## 3. TDD execution

Test list (14 behaviors + 021 regression) per design §5; suite verified true-RED on v1 code
(12 failed / 3 acceptance guards passed) before any implementation. Single GREEN pass:
15/15. Regression: feature_021 30/30 green. Structural guard
`test_thought_pattern_identical_in_both_plugins` pins the two pattern copies byte-exact
(incl. the `--` opener — design §1 literal corrected during test writing, predated A2's `.sql`).

## 4. Known limitations (accepted per design/analysis)

- Residual FP: `omt_think.ts`'s own prose comment `// TA: tags remain the source of truth` matches
  the anchor — file is correctly gated anyway (real xref thought at EOF).
- Parity heuristic can false-refuse (delimiter inside a single-quoted string) — safe direction;
  user picks another line.
- `.ts` template-literal context not guarded (Tier A scope; documented in `inStringContext`).
- `omt_done` full-suite gate is unreachable while pre-existing feature_018 react_screen failures
  (3, Textual/mock, unrelated) persist; phase exit proceeded via `omt_complete` (feature_021 prior
  art). The 2 tdd_check subprocess tests are live-ledger-sensitive by design and only pass when no
  TDD session is in-window — verified green after phase advance cleared `tdd_mode`.

## 5. Verification

- 15/15 feature_022 tests; 30/30 feature_021; feature_020 + feature_016 + scripts/omt suites green
  (modulo the §4 state-sensitive pair, green post-advance).
- MVC++ lint baseline unchanged (no `src/` business code).

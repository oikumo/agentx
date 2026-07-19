# Operation Spec: Think Anywhere V2 — Tier Remainder new/modified operations

> Companion to `design_004_tier_b2_e1_e2.md` (2026-07-18). Signatures + contracts only.

---

## `omt_think_suggest(path, top?) -> str` (NEW, omt_think.ts)

- **path** (string, required): repo-relative or absolute `.py` file (must exist; not protected).
- **top** (number, optional): max sites returned. Default 5, clamped to [1, 20], `Math.floor`.
- **Returns** (plain string, one of):
  - Ranked list: `💡 TA: suggest — <rel>: <N> candidate site(s), <M> already covered.\n`
    + ` i. L<line> <Kind> → insert after L<end>: \`<preview>\`` per site
    + footer `\n→ omt_think{path:"<rel>", line:<end>, thought:"..."}  (or after:"<preview>" — unique-match caveat)`
  - Empty: `💡 TA: suggest — <rel>: 0 candidate sites (<M> covered). Nothing to suggest.`
  - Refusals: missing `path` (`❌`); protected; nonexistent; non-`.py` (names ext);
    unparseable Python / spawn failure (`⛔ TA: suggest refused — …`).
- **Ranking:** paper table Assign(1) > Return(2) > Expr(3) > If(4) > AugAssign(5),
  tie-break source line ascending.
- **Coverage exclusion:** a site is excluded when an anchored thought line
  (`THOUGHT_PATTERN`) exists at site.line ± 1; excluded count reported as `M`.
- **Side effects:** NONE (no file writes, no index writes, no ledger records).
- **Mechanism:** `execFileSync("uv", ["run","--no-sync","python","-c",SCRIPT,abs])`,
  60s timeout; JSON stdout `[{line,end,kind}]`; `end` (`end_lineno`) is the
  splice-safe insertion line for multi-line statements.

## `omt_think_reindex(path?) -> str` (NEW, omt_think.ts)

- **path** (string, optional): restrict reconciliation to one repo-relative file's
  records; default = every recorded path.
- **Returns**: `🧹 TA: reindex — kept K, repaired R, dropped D, verify-pruned V`
  (`; skipped S path(s)` appended only when S>0) + ≤10 detail lines
  `<path>: <old>→<new> (<preview>)`.
- **Disposition per add-record:** live-same-line-same-text → keep; unique text match
  elsewhere in file → repair (gains `repaired_from`); text gone / file missing /
  ambiguous (>1 match) → drop. Latest add per `path:line` slot wins (dedupe → dropped).
- **Verify prune:** verify records whose slot has no surviving add-record → dropped.
  Unknown `kind`s pass through untouched.
- **Side effects:** rewrites `.meta/.omt/thoughts.jsonl` only (fail-open I/O).
  Idempotent. Never touches source files, never records consults.

## `omt_think(path, thought, line?|after?|symbol?, category?) -> str` (unchanged)

## `omt_think_list / omt_think_remove / omt_think_verify` (unchanged)

## Tool map + permissions (wiring delta)

- `omt_think.ts` default factory: `tool: { omt_think, omt_think_list, omt_think_remove, omt_think_verify, omt_think_suggest, omt_think_reindex }` (ONE write).
- `opencode.jsonc`: +`"omt_think_suggest": "allow"`, +`"omt_think_reindex": "allow"`.
- e2e literal asserts updated in RED phase (tests hat): `test_omt_harness_e2e.py:190`
  (+jsonc allows), feature_021 `test_omt_think.py:83-89` (rename `..._with_four_tools`
  → `..._with_six_tools`).

## Theory doc (E2 — content fixes, not an operation)

`.meta/doc/harness/think_anywhere_langchain.md`: F10 paren; F11 unbiased pass@k
(`math.comb`, n≥k, sampler drops `k`); F12 per-block prefix-parse attribution;
F13 strip-validation + mid-statement risk + sandbox warning + dead-stub removal.
Guard: all ```python fences `ast.parse` (test 16).

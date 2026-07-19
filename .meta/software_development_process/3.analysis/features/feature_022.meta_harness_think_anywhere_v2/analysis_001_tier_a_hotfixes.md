# Analysis 001: Think Anywhere V2 — Tier A Correctness Hotfixes

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_022.meta_harness_think_anywhere_v2
> **Source:** `2.requirements/.../feature_022.meta_harness_think_anywhere_v2/FEATURE.md` (13-flaw evaluation, tiers A–E)

## Scope decision (2026-07-18)

**Tier A only** (A1–A4 from FEATURE.md §"Proposed improvements"). Tiers B–E are deferred to
follow-up features; this feature must not preclude them (anchor-ready pattern, index kept).

Rationale: Tier A fixes the only flaw already observed corrupting a production file (F1) plus
all confirmed false-positive/robustness noise, at small diff size, with no new tool surface.

## Verified evidence (every claim re-checked against source, 2026-07-18)

| Fix | Flaw | Verified evidence |
|-----|------|-------------------|
| A1 | F3 gate/retrieval false positives | `omt_enforcer.ts:232` greps substring `"TA:"`; `omt_think.ts:130` (dead fn), `:229-231` (list), `:291` (digest) same. Measured: current pattern = **220 hits** repo-wide; anchored `^\s*(#|//|/\*|<!--)\s*TA:` = **5 hits** (4 true thoughts + 1 incidental, see below). |
| A1b | missing excludes (new finding) | `grepThoughts` excludes only `.git/node_modules/.omt/*.env*` — **`.venv`, `__pycache__` not excluded** → binary-match warnings + site-packages `DATA:`/`META:` noise inflate the digest. |
| A2 | F2 unsafe `#` default | `omt_think.ts:50-51`: `// default: hash is safe for most text formats` → `return { open: "#" }` for ALL unknown extensions. |
| A3 | F1 string-unaware insertion | Self-documented in production: `main_screen.py:78` (`TA: gotcha: omt_think on a line inside a triple-quoted CSS string inserts # which breaks Textual CSS parser`). Insert path `omt_think.ts:195-206` splices by raw line number, zero lexical checks. |
| A4 | F7 sloppy filters | `omt_think.ts:229-231`: dead ternary (`category ? x : x`), `query` interpolated unescaped into grep regex, `category` not lowercased (insert `:150` writes raw too — both sides must lowercase). |
| A4 | F9 dedup / CRLF | `omt_think.ts:191-206`: no (path, thought) dedup; `split("\n")` leaves `\r` on CRLF lines → inserted TA line is LF-only → mixed endings. |

**New finding (dead code):** `fileThoughts` (`omt_think.ts:124-141`) has zero call sites — the
enforcer uses its own `fileThoughtsIn`. Remove it in A1 (its substring grep is a third copy of
the F3 bug; deleting is smaller than fixing).

**Residual false positive (accepted):** `omt_think.ts:64` — a prose comment line that genuinely
starts `// TA: tags remain…` (continuation of a block comment). Syntactically indistinguishable
from a thought at grep level; acceptable (file also carries a real thought at `:316`, so it is
correctly gated regardless). Rewording that comment is out of scope.

## Problem analysis per hotfix

### A1 — Anchor retrieval/gate pattern to real comment syntax (+ excludes)
Pattern: `^\s*(#|//|/\*|<!--)\s*TA:` (grep `-E`). Matches every line `buildThoughtLine` can emit
(`#`, `//`, `/* … */`, `<!-- … -->`); rejects prose, `META:`/`DATA:` substrings, code mentions.
Apply at 4 sites:
1. `omt_enforcer.ts fileThoughtsIn` (think-gate) — kills gate noise on docs/harness files.
2. `omt_think.ts grepThoughts` (list + digest) — digest count becomes truthful (220 → 4).
3. `omt_think.ts omt_think_remove` line check `:279` (`includes("TA:")` → anchored regex) so a
   prose line can't be "removed" as a thought.
4. Delete dead `fileThoughts` (`:124-141`).
Companion: add `--exclude-dir=.venv --exclude-dir=__pycache__` to `grepThoughts`.
Category filter composes: `^\s*(#|//|/\*|<!--)\s*TA:\s*<cat>:` (escaped, lowercased).

### A2 — Extension safety
`commentSyntaxFor`: add explicit maps — `//`-family: `.go .rs .java .c .cpp .h .hpp .cs .swift
.kt .scala`; `--`-family: `.sql`; `<!-- -->`-family: `.html .xml .vue .svelte`. **Unknown →
`null`** → existing refusal path (`:188-190`) fires. Delete the false "safe default" comment.
Denylist unchanged (`.env*`, README, uv.lock, LICENSE, `.json`).

### A3 — String-context insertion guard
Refuse insertion when the target line falls inside a string/fence context, per extension:
- `.py`: triple-quote parity heuristic — count unescaped `"""`/`'''` occurrences in lines
  `[0, insertAt)`; odd count of either delimiter ⇒ inside a string ⇒ refuse. (FEATURE.md
  sanctions the cheap heuristic; full `tokenize` would need a Python subprocess — rejected.)
- `.md`/`.mdx`: fence parity — odd count of ` ``` ` openers before `insertAt` ⇒ inside code
  fence ⇒ refuse.
- All other extensions: no guard in Tier A (repo's thought targets are `.py/.md/.ts`; `.ts`
  template literals deferred — documented limitation).
Guard runs AFTER extension/protected/exists checks, BEFORE splice. Refusal message names the
reason and suggests anchoring below the string (mirrors existing ⛔ UX).

### A4 — Filter/dedup/EOL hygiene
- Lowercase `category` at insert (`buildThoughtLine`) and at filter (`omt_think_list`).
- Regex-escape `query` before interpolation; delete dead ternary.
- Dedup: refuse if the normalized thought (whitespace-collapsed, `TA:`-stripped) already
  exists in the target file (anchored-grep compare) — message points at existing line.
- EOL: detect dominant line ending (`\r\n` present ⇒ CRLF); join with detected EOL so the
  inserted line matches the file (fixes mixed endings; LF files unchanged).

## Static path sketch (what changes)

```
omt_think.ts
  ~ commentSyntaxFor(ext)      + explicit maps, unknown → null            (A2)
  ~ grepThoughts(pattern,tgt)  + .venv/__pycache__ excludes               (A1b)
  ~ omt_think.execute          + string-guard, dedup, EOL-join, lc cat    (A3,A4)
  ~ omt_think_list.execute     anchored pattern, escaped query, lc cat    (A1,A4)
  ~ omt_think_remove.execute   anchored line check                        (A1)
  - fileThoughts(rel)          DELETED (dead code)                        (A1)
  + THOUGHT_PATTERN (const)    single source: ^\s*(#|//|/\*|<!--)\s*TA:   (A1)
  + inStringContext(lines,at,ext) -> boolean                              (A3)

omt_enforcer.ts
  ~ fileThoughtsIn(absFile)    anchored grep pattern                      (A1)

(no changes: thinkGateDecision, hasConsultedThoughts, index format, tool surface)
```

## Risks / non-goals

- **Anchored pattern must match ALL v1-emitted forms** — a thought the gate can no longer see
  would silently un-gate a file. Mitigation: test every `commentSyntaxFor` family round-trip.
- **Triple-quote heuristic is not a parser** — a `"""` inside a single-quoted string defeats
  parity counting; accepted (heuristic sanctioned by FEATURE.md; failure mode = refuse, which
  is safe-direction).
- Non-goals (deferred): anchors/symbol insertion (B), verify lifecycle (C), read-time
  injection (D), index strategy + theory-doc fixes (E), `.ts` template-literal guard.

## Test strategy (pointer for Design)

Reuse feature_021 harness: `_think_runner.mjs` / `_think_gate_runner.mjs` node runners invoked
from pytest (`tests/features/feature_021…/test_omt_think.py`, 30 tests green). New suite:
`tests/features/feature_022.meta_harness_think_anywhere_v2/` — TDD per feature_016
(major_feature ⇒ auto-TDD in Programming).

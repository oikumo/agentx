# Design 001: Meta Harness Think Anywhere

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_021.meta_harness_think_anywhere
> **Source theory:** `.meta/doc/harness/think_anywhere_langchain.md`

This feature is **tooling/enforcement**, not an MVC++ screen, so the design doc uses plugin
functions + a pure decider in place of the View/Model/Controller triad. The MVC++ self-check
at the end is N/A (no `src/` business code touched); the architectural rules that *do* apply
(plugin loader contract, opencode ToolResult contract, execFileSync safety) are called out
inline and enforced by the feature_020-style test suite.

## Components / surfaces affected

| Surface | Change | Gated? |
|---|---|---|
| `.opencode/plugin/omt_think.ts` | **NEW** standalone plugin: 3 tools + session.start digest | harness-e2e guard |
| `.opencode/plugin/omt_enforcer.ts` | **ADD** pure `thinkGateDecision` + `hasConsultedThoughts` + before-hook integration | harness-e2e guard |
| `opencode.jsonc` | allow `omt_think`, `omt_think_list`, `omt_think_remove` | harness-e2e guard |
| `AGENTS.md` | new "Think Anywhere (feature_021)" MANDATORY section | harness-e2e guard |
| `.meta/META_HARNESS.md` | new `SECTION:THINK` + `THINK_*` tags + `CMD_THINK_*` | harness-e2e guard |
| `.meta/.omt/thoughts.jsonl` | **NEW** append-only index (gitignored runtime state) | n/a (runtime) |
| `tests/features/feature_021.../` | **NEW** TDD + e2e test suite + node runners | tests (canary via TDD) |
| `tests/scripts/omt/test_omt_harness_e2e.py` | extend HARNESS_FILES + 1 check for omt_think | exempt (self) |

## 1. Tag format specification

A **thought** is a single-line, language-valid comment whose content starts with the marker `TA:`.

```
<lang-comment-prefix> TA: [<category>: ] <free-form thought>
```

- Marker is always the literal `TA:` (grep-uniform across languages; mirrors `SECTION:`/`RULE_`).
- `category` is optional, free-text lowercase token: `gotcha`, `why`, `risk`, `xref`, `todo`, …
  Embedded inline as `TA: gotcha: ...` so `grep "TA: gotcha:"` filters by category.
- One line only (token-minimal; multi-line thoughts split into multiple `TA:` lines).

Per-language comment syntax (the only thing that varies):

| Extension(s) | Comment form |
|---|---|
| `.py` `.toml` `.cfg` `.ini` `.sh` `.yml` `.yaml` | `# TA: ...` |
| `.ts` `.js` `.mjs` `.cjs` `.tsx` `.jsx` | `// TA: ...` |
| `.md` `.mdx` | `<!-- TA: ... -->` |
| `.jsonc` | `// TA: ...` |
| `.css` | `/* TA: ... */` |
| `.json` | **DENIED** (no comments — would break parsing) |
| other/unknown | `# TA: ...` (default; safe for most text formats) |

`omt_think` computes the prefix from the target extension; `null` extension → default `#`.

## 2. Tool specifications (`.opencode/plugin/omt_think.ts`)

Standalone plugin, same contract as `omt_nav.ts` / `omt_status.ts`:
- `import { tool } from "@opencode-ai/plugin"`; `args` + `tool.schema.*` (DEFECT-C safe).
- `async execute(args, context)` returns a **plain string** (DEFECT-D safe).
- Default export `async () => ({ tool: {...}, "session.start": ... })`.
- NO named exports of tool objects (DEFECT-A safe); only the default factory.
- File ops use `execFileSync`/`readFileSync`/`writeFileSync` (no shell strings — H3 safe).

### 2.1 `omt_think` — add a thought
```
args:
  path      string  REQUIRED  repo-relative target file
  thought   string  REQUIRED  the thought text (single line; newlines stripped)
  line      number  optional  1-based line to insert AFTER (default: append at EOF)
  category  string  optional  lowercase token (gotcha|why|risk|xref|todo|...)
returns: string  "✅ TA: … → <path>:<line>"
behavior:
  1. resolve rel; if isProtectedPath(rel) → deny message (list protected set)
  2. ext = path.extname(rel); if ext==='.json' → deny "JSON has no comments"
  3. prefix = commentSyntaxFor(ext); thought = single-line, strip "TA:" if user prepended
  4. read file (if missing → create? NO: deny "file does not exist" — never invent files)
  5. insert line `<prefix> TA: [:<category>: ]<thought>` after `line` (or push to EOF)
  6. write file back (utf8)
  7. appendIndex({ts, path:rel, line:newLineNo, category, thought})
  8. return compact confirmation
```

### 2.2 `omt_think_list` — retrieve thoughts (grep-backed, authoritative inline)
```
args:
  path      string  optional  restrict to a file/dir (default: whole repo, non-protected)
  category  string  optional  filter `TA: <category>:`
  query     string  optional  extra substring filter
returns: string  "<path>:<line>: TA: ...\n…" (+ trailing "N thoughts" count)
behavior:
  1. build grep pattern: base `TA:`; if category → `TA: <category>:`; if query → `TA:.*<query>`
  2. execFileSync('grep', ['-rn','--', pattern, <target>]) on path or repo root
     - exclude .meta/.omt/, node_modules, .git, *.env* via grep --exclude/--exclude-dir
  3. parse `file:line:content`, render `rel:line: content` (mirrors omt_nav render)
  4. cap output at 50 lines + "… (N total, run omt_think_list <filter> for more)" if truncated
  5. record consult in ledger: appendLedger({kind:'think_consult', session})
  6. return string
```
Note: `omt_think_list` is also usable as plain `grep -rn "TA:" <path>` — the tool is a
convenience that also marks the session consulted (clearing the think-gate).

### 2.3 `omt_think_remove` — remove a thought
```
args:
  path   string  REQUIRED  target file
  line   number  REQUIRED  1-based line of the TA: comment to remove
returns: string  "🗑 removed TA: at <path>:<line>"
behavior:
  1. deny if protected; read file; assert lines[line-1] contains 'TA:' (else error)
  2. remove that line; write back
  3. best-effort index reconcile: rewrite index without the matching {path,line} record
  4. return confirmation
```

### 2.4 `session.start` — mechanical per-session digest
```
behavior (every session, token-minimal):
  1. grep -rn 'TA:' across repo (excludes: .git, node_modules, .meta/.omt, *.env*)
  2. parse hits; total = N
  3. render: "💡 THINK-ANYWHERE (feature_021): N thoughts indexed across M files."
     + first min(N,30) hits as `rel:line: content`
     + if N>30: "… (+N more: omt_think_list)"
     + reminder: "Drop new thoughts with omt_think{path,thought}; review before editing
       thought-carrying files (think-gate)."
  4. if N==0: "0 thoughts yet. Add one with omt_think{path,thought} when you learn a gotcha."
returns: string  (surfaced by opencode as the session.start message)
```

## 3. Think-gate (`.opencode/plugin/omt_enforcer.ts`)

A pure, exported decider mirroring `navGateDecision`:

```ts
export function thinkGateDecision(opts: {
  hasThoughts: boolean     // does the target file contain TA: lines?
  consulted: boolean       // has the session consulted thoughts (ledger think_consult)?
}): "allow" | "block"
```
- `hasThoughts=false` → "allow" (no thoughts to review).
- `hasThoughts=true && consulted` → "allow".
- `hasThoughts=true && !consulted` → "block".

**Integration** in `tool.execute.before` (EDIT_TOOLS only, after the existing protected/e2e/
tests/src checks pass — i.e. only for edits that are already permitted):
```
const rel = ...  // already computed
if (rel.endsWith('.py') || isTextFile(rel)) {           // cheap skip for binary
  const thoughts = fileThoughts(rel)                    // grep TA: in this one file
  if (thoughts.length) {
    const consulted = hasConsultedThoughts(session)     // ledger read
    if (thinkGateDecision({hasThoughts:true, consulted}) === 'block')
      throw new OmtBlock(thinkGateMsg(rel, thoughts))   // shows the file's TA: lines
  }
}
```
- `fileThoughts(rel)`: `execFileSync('grep','-n','--','TA:', absFile)` → string[] (cheap, one file).
- `hasConsultedThoughts(session)`: reads ledger for `kind:'think_consult'` (exact session, else
  within UNLOCK_WINDOW_MS) — mirrors `hasNavUnlock`.
- **NOT bypassable by `omt_skip`**: thoughts are safety-relevant. Only `omt_think_list`
  (which writes `think_consult`) or hitting the block (which surfaces the thoughts) clears it.
  To avoid an infinite loop, the block itself does NOT write `think_consult`; the agent must
  call `omt_think_list` (active consult) — but the block message already shows the file's
  thoughts, so the agent has read them; the expected next action is `omt_think_list{path:rel}`
  which both re-reads and clears the gate. (Documented in the block message.)

> Rationale for "block doesn't clear": keeps consult explicit/audited in the ledger, and the
> block message already contains the thoughts so no information is lost on the retry.

## 4. JSONL index (`.meta/.omt/thoughts.jsonl`)

Append-only, gitignored (same dir as `ledger.jsonl`). One JSON object per line:
```json
{"ts":"2026-07-16T...Z","path":"src/agentx/agent/core.py","line":42,"category":"gotcha","thought":"mutates history in place"}
```
- Inline `TA:` tags are the **source of truth**; the index is a best-effort structured filter.
- `omt_think_list` always greps inline (authoritative); the index is not read by list in v1
  (kept simple — grep is sufficient and avoids drift bugs). Index value: future structured
  tooling / analytics. Kept in sync on add/remove by `omt_think`/`omt_think_remove`.

## 5. Guardrails summary

- **Hard-deny insert/remove:** `.env*`, `README.md`, `uv.lock`, `LICENSE`, `.json`.
- **`omt_think` never creates a file** that doesn't exist (no phantom files).
- **`omt_think` bypasses phase/canary gates** (annotation, not functional change) — deliberate.
- **Think-gate is not skip-bypassable**; cleared only by `omt_think_list` / consult.
- **Token budget** (§Analysis table): all retrieval O(hits); digest capped at 30; list capped at 50.

## 6. File map (exact paths created/modified)

NEW:
- `.opencode/plugin/omt_think.ts`
- `.meta/.omt/thoughts.jsonl` (runtime, gitignored — created on first `omt_think`)
- `tests/features/feature_021.meta_harness_think_anywhere/test_omt_think.py`
- `tests/features/feature_021.meta_harness_think_anywhere/_think_runner.mjs`
- `tests/features/feature_021.meta_harness_think_anywhere/_think_gate_runner.mjs`

MODIFY:
- `.opencode/plugin/omt_enforcer.ts` (add think-gate, ~40 lines)
- `opencode.jsonc` (3 allow entries)
- `AGENTS.md` (new MANDATORY section)
- `.meta/META_HARNESS.md` (SECTION:THINK + tags)
- `tests/scripts/omt/test_omt_harness_e2e.py` (HARNESS_FILES + 1 check)

## 7. Test plan (TDD testlist — behaviors to implement)

Tests live in `tests/features/feature_021.meta_harness_think_anywhere/test_omt_think.py`,
mirroring feature_020's structure (structural + behavioral-via-node + pure-decider + e2e).

**Structural (source-string):**
1. `omt_think.ts` exists & exports default async factory; tool map has the 3 tools.
2. Uses canonical `args`/`tool.schema` (DEFECT-C); returns strings (DEFECT-D); execFileSync (H3).
3. `commentSyntaxFor` covers py/ts/md/jsonc/css/json(denied)/default.
4. `isProtectedPath` denies the PROT_FILES set + `.json`.
5. Enforcer exports `thinkGateDecision` + `hasConsultedThoughts`; AGENTS.md has the MANDATORY
   section; META_HARNESS has SECTION:THINK; opencode.jsonc allows the 3 tools.

**Behavioral (invoke REAL tools via `_think_runner.mjs`):**
6. `omt_think` on a temp `.py` file inserts `# TA: …` at EOF; returns path:line.
7. `omt_think` with `line` inserts AFTER that line.
8. `omt_think` with `category` produces `TA: gotcha: …`.
9. `omt_think` on `.env` → denied; on `README.md` → denied; on `.json` → denied.
10. `omt_think` on non-existent file → denied.
11. `omt_think_list` returns the `TA:` line just added (path:line: content).
12. `omt_think_list` with `category` filters; with `query` filters; capped at 50.
13. `omt_think_list` writes `think_consult` to the ledger.
14. `omt_think_remove` removes the line; `omt_think_list` no longer returns it.
15. ts/md/jsonc comment syntax produced correctly.

**Pure decider (`_think_gate_runner.mjs` → `thinkGateDecision`):**
16. `hasThoughts=false` → allow.
17. `hasThoughts=true, consulted=false` → block.
18. `hasThoughts=true, consulted=true` → allow.

**Enforcer integration (source + ledger):**
19. `hasConsultedThoughts` reads `think_consult` ledger records (exact session + window fallback).
20. before-hook calls `thinkGateDecision` for EDIT_TOOLS on files with `TA:` (source presence).

**e2e (extend `test_omt_harness_e2e.py` + a serve-load check):**
21. `omt_think.ts` added to HARNESS_FILES; e2e asserts plugin loads (default export) + 3 tools
    registered. (serve-level load verified by feature_020's `test_opencode_e2e.py` pattern,
    reused here via a small spawn-serve assertion or, if serve is flaky, the schema-runner
    pattern from feature_020 `TestToolSchemaReal`.)

## 8. Operation specifications

```python
def omt_think(path, thought, line=None, category=None) -> str:
    """
    Operation: insert a language-aware TA: thought-tag inline in a non-protected file.

    Preconditions:
      - path is repo-relative and the file exists.
      - path is not in the protected set (.env*, README.md, uv.lock, LICENSE) and not .json.
    Exceptions:
      - protected path: returns a deny string (no write).
      - .json / unsupported: returns a deny string.
      - missing file: returns an error string (never creates files).
    Postconditions:
      - exactly one <prefix> TA: ... line inserted after `line` (or EOF).
      - .meta/.omt/thoughts.jsonl appended with {ts,path,line,category,thought}.
    """

def omt_think_list(path=None, category=None, query=None) -> str:
    """
    Operation: grep-backed retrieval of TA: thoughts; marks the session consulted.

    Preconditions: none (whole-repo if path absent).
    Exceptions: none (empty → "0 thoughts").
    Postconditions:
      - returns 'file:line: TA: ...' lines (capped 50) + count.
      - ledger appended with {kind:'think_consult', session}.
    """

def omt_think_remove(path, line) -> str:
    """
    Operation: remove a TA: comment line and reconcile the index.

    Preconditions: file exists; lines[line-1] contains 'TA:'.
    Exceptions: protected path / not-a-TA line → error string (no write).
    Postconditions: line removed; index rewritten without the matching record.
    """
```

## 9. MVC++ self-check (N/A — no src/ business code)

- [x] N/A: no Model/View/Controller touched. Feature is opencode tooling/enforcement.
- [x] `uv run scripts/omt/mvc_check.py` continues to pass (no src/ changes).
- [x] Plugin loader contract honored (default export, args schema, string returns, execFileSync).
- [x] Think-gate is pure + exported (unit-testable without opencode, like navGateDecision).

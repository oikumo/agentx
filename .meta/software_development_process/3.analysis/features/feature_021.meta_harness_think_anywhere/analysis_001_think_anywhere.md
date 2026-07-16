# Analysis 001: Meta Harness Think Anywhere

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_021.meta_harness_think_anywhere
> **Source theory:** `.meta/doc/harness/think_anywhere_langchain.md`

## Problem / domain concepts

The Think-Anywhere paper interleaves *ephemeral* `<thinkanywhere>` reasoning blocks inside
generated code, then strips them to get executable code. The agentx META HARNESS has the
**opposite temporal problem**: the agent operates across many sessions and context windows,
and re-derives the same non-obvious facts (gotchas, "why this is here", cross-references,
risks) every time by re-reading whole files — expensive in tokens and lossy.

**Adaptation:** make the reasoning blocks *persistent and inline* in the real files, as
grep-friendly `TA:` comment tags. Retrieval is then O(hits) tokens via the standard
`grep`/`glob` tools (no whole-file reads), and a per-session digest guarantees the agent
sees accumulated context at session start.

Key entities:
- **Thought** — a single-line, language-valid comment whose content starts with `TA:`.
  Carries: target file, line, free-form text, optional category, timestamp, author=agent.
- **Index** — append-only JSONL sidecar (`.meta/.omt/thoughts.jsonl`) mirroring inline tags
  for structured queries (by category/feature/path). Inline tags are the source of truth;
  the index is a best-effort accelerator.
- **Think-gate** — a pure decision over `{file has TA: thoughts, session has consulted}`
  that blocks edits to thought-carrying files until consulted (mirrors feature_020 nav-gate).
- **Digest** — session.start grep of `TA:` across the repo, capped to stay token-minimal.

Relationship to existing harness:
- Reuses the **tag-prefix convention** (`SECTION:`, `RULE_`, …) — `TA:` is a new prefix.
- Reuses the **ledger** (`.meta/.omt/ledger.jsonl`) for consult tracking (`kind:"think_consult"`).
- Reuses the **standalone-plugin pattern** (omt_status.ts / omt_nav.ts) for `omt_think.ts`.
- Reuses the **pure-decision + before-hook** pattern (navGateDecision) for the think-gate.

## Analysis class sketch (static path)

This feature is tooling/enforcement, not a domain model — there are no persistent business
classes. The "classes" are plugin functions and a pure decider:

```
omt_think.ts (standalone opencode plugin)
  + omt_think(path, thought, line?, category?)  -> string   // insert + index
  + omt_think_list(path?, category?, query?)     -> string   // grep retrieval + consult mark
  + omt_think_remove(path, line?)                -> string   // remove + reconcile
  + session.start()                              -> string   // digest
  - commentSyntaxFor(ext)                        -> string|null
  - isProtectedPath(rel)                         -> boolean
  - appendIndex(record)                          -> void

omt_enforcer.ts (existing, minimal addition)
  + thinkGateDecision({hasThoughts, consulted})  -> "allow" | "block"   // pure, exported
  + hasConsultedThoughts(session)                -> boolean             // ledger read
  - fileThoughts(rel)                            -> string[]            // grep TA: in one file

.meta/.omt/thoughts.jsonl (append-only index)
  { ts, path, line, category, thought }
```

## Token-budget analysis (core non-functional requirement)

| Operation | Token cost | Mechanism |
|---|---|---|
| Add a thought | O(1) tool call, ~1 line written | `omt_think` inserts one comment line |
| Retrieve by path/category/query | O(hits) | `omt_think_list` returns `file:line: TA: …` only |
| Retrieve via standard tools | O(hits) | `grep -n "TA:" <path>` (no plugin needed) |
| Session digest | O(min(N, cap)) | session.start greps `TA:`, caps at ~30 lines + count |
| Think-gate block message | O(thoughts in that file) | shows only that file's `TA:` lines |

Whole-file reads are never required to recover thoughts — this is the key token win over
"re-read the file to remember what's tricky".

## Guardrails (from user requirement: "anywhere except protected")

- **Denied (hard):** `.env*`, `README.md`, `uv.lock`, `LICENSE` (the PROT_FILES set).
- **Denied (syntax):** `.json` (no comments); `.jsonc` allowed (comments are valid).
- **Allowed without a phase:** `TA:` insertion is an annotation, not a functional change, so
  `omt_think` bypasses the phase/canary gates (it is a custom tool, not in EDIT_TOOLS). This
  realises "anywhere except protected". Documented as a deliberate exception.
- **Think-gate is NOT bypassable by omt_skip** — thoughts are safety-relevant warnings; only
  `omt_think_list` (or the block's own surfacing) clears the consulted flag.

## Open questions (resolved before Design)

- *Should the digest grep the whole repo every session start?* → Yes, but capped (~30 lines +
  total count) and restricted to non-protected, non-binary files. Cheap because `TA:` hits are
  sparse.
- *Index drift if a `TA:` tag is edited/deleted by hand?* → Inline is source of truth; index
  is best-effort. `omt_think_list` always greps inline (authoritative), index is an optional
  structured filter. A `omt_think_list --reindex` not needed for v1; reconcile on remove.
- *Does the think-gate fire for new files (no thoughts)?* → No: `hasThoughts=false → allow`.
- *Interaction with the harness e2e edit-guard?* → `omt_think` inserting into harness-surface
  files dirties them; that is acceptable (non-functional). The think-gate itself is part of the
  enforcement surface and will be covered by the e2e test.

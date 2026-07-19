# Operation Spec: Think Anywhere V2 — Tier A modified operations

> Operation specifications for feature_022.meta_harness_think_anywhere_v2 — `omt_agent_guide.md §10`.
> Only operations whose contracts CHANGE are specified here (deltas vs feature_021's spec).
> Unchanged: `thinkGateDecision`, `hasConsultedThoughts`, `session.start` digest shape.

## `omt_think(path, thought, line?, category?) -> str` (modified)

```python
def omt_think(path, thought, line=None, category=None) -> str:
    """
    Operation: insert a language-aware TA: thought-tag inline in a non-protected file.

    Preconditions:
      - path is repo-relative; target file already exists.
      - path not protected (.env*, README.md, uv.lock, LICENSE) and not .json.
      - extension has an EXPLICIT comment-syntax mapping (no default).            # A2

    Exceptions (deny strings; no write occurs):
      - protected path / .json / missing file: as v1.
      - unknown extension: deny string naming the ext; suggests adding a mapping. # A2
      - insertion point inside a triple-quoted string (.py) or code fence (.md):  # A3
        deny string naming file:line and the F1 hazard.
      - duplicate (path, normalized thought, category): deny string pointing      # A4
        at the existing line.
      - line out of range: clamps to EOF (unchanged).

    Postconditions:
      - exactly one `<prefix> TA: [<category>: ]<thought>` line inserted; category
        lowercased.                                                             # A4
      - file's dominant EOL preserved (CRLF file → CRLF thought line).          # A4
      - thoughts.jsonl appended with {ts, path, line, category, thought}.
      - returns "✅ TA: … → <path>:<line>".
    """
```

## `omt_think_list(path?, category?, query?) -> str` (modified)

```python
def omt_think_list(path=None, category=None, query=None) -> str:
    """
    Operation: grep-backed retrieval of TA: thoughts; marks the session consulted.

    Preconditions: none (whole-repo search when path absent).

    Exceptions: none; empty result returns a "0 thoughts" message.

    Postconditions:
      - only lines matching ^\\s*(#|//|/\\*|<!--)\\s*TA: are returned — prose,     # A1
        META:/DATA: substrings, and code mentions never match.
      - category filter is case-insensitive (lowercased both sides).             # A4
      - query is regex-escaped before use (metacharacters are literal).          # A4
      - search excludes .git, node_modules, .meta/.omt, *.env*, .venv,
        __pycache__.                                                             # A1b
      - ledger appended with {kind:'think_consult', session} (unchanged).
      - output capped at 50 lines (unchanged).
    """
```

## `omt_think_remove(path, line) -> str` (modified)

```python
def omt_think_remove(path, line) -> str:
    """
    Operation: remove a TA: comment line and reconcile the index.

    Preconditions:
      - file exists; lines[line-1] matches the anchored thought pattern.         # A1

    Exceptions:
      - protected path: deny string; no write.
      - line does not match the anchored pattern (incl. prose mentioning TA:):
        error string; no write.                                                  # A1

    Postconditions:
      - the TA: line is removed; file written back (EOL round-trip unchanged).
      - thoughts.jsonl rewritten without the matching {path,line} record.
      - returns "🗑 removed TA: at <path>:<line>".
    """
```

## `fileThoughtsIn(absFile) -> [{line, content}]` (enforcer; modified)

```python
def fileThoughtsIn(absFile: str) -> list:
    """
    Operation: detect thought-carrying files for the think-gate before-hook.

    Preconditions: absFile is an absolute path (may not exist → []).

    Exceptions: none (grep failure → []).

    Postconditions:
      - returns hits for anchored TA: comment lines ONLY — the gate no longer    # A1
        fires on prose, META:/DATA: substrings, or code mentions.
      - detects every line form omt_think can emit (round-trip guarantee).       # A1
    """
```

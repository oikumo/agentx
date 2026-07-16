# Operation Spec: Think Anywhere tools

> Operation specifications for feature_021.meta_harness_think_anywhere — `omt_agent_guide.md §10`.
> These are opencode plugin tool operations (not Controller methods); the docstring contract
> (preconditions / exceptions / postconditions) still applies.

## `omt_think(path, thought, line?, category?) -> str`

```python
def omt_think(path, thought, line=None, category=None) -> str:
    """
    Operation: insert a language-aware TA: thought-tag inline in a non-protected file.

    Preconditions:
      - path is repo-relative and the target file already exists.
      - path is not protected (.env*, README.md, uv.lock, LICENSE) and not .json.

    Exceptions:
      - protected path: returns a deny string; no write occurs.
      - .json (no comments) or unsupported: returns a deny string.
      - missing file: returns an error string; never creates a new file.
      - line out of range: clamps to EOF.

    Postconditions:
      - exactly one `<prefix> TA: [:<category>: ]<thought>` line inserted after `line`
        (or appended at EOF).
      - .meta/.omt/thoughts.jsonl appended with {ts, path, line, category, thought}.
      - returns a compact "✅ TA: … → <path>:<line>" string.
    """
```

## `omt_think_list(path?, category?, query?) -> str`

```python
def omt_think_list(path=None, category=None, query=None) -> str:
    """
    Operation: grep-backed retrieval of TA: thoughts; marks the session consulted.

    Preconditions:
      - none (whole-repo search when path absent).

    Exceptions:
      - none; empty result returns a "0 thoughts" message.

    Postconditions:
      - returns "<rel>:<line>: TA: ..." lines, capped at 50, plus an "N thoughts" count.
      - ledger appended with {kind:'think_consult', session} — clears the think-gate.
      - excludes .git, node_modules, .meta/.omt, *.env* from the search.
    """
```

## `omt_think_remove(path, line) -> str`

```python
def omt_think_remove(path, line) -> str:
    """
    Operation: remove a TA: comment line and reconcile the index.

    Preconditions:
      - file exists; lines[line-1] contains the 'TA:' marker.

    Exceptions:
      - protected path: deny string; no write.
      - line is not a TA: line: error string; no write.

    Postconditions:
      - the TA: line is removed; file written back.
      - .meta/.omt/thoughts.jsonl rewritten without the matching {path,line} record.
      - returns "🗑 removed TA: at <path>:<line>".
    """
```

## `thinkGateDecision({hasThoughts, consulted}) -> "allow" | "block"`

```python
def thinkGateDecision(hasThoughts: bool, consulted: bool) -> str:
    """
    Operation: pure decision — may the agent edit a file that carries TA: thoughts?

    Preconditions:
      - hasThoughts: does the target file contain >=1 TA: line?
      - consulted: has the session an active think_consult ledger record?

    Exceptions: none (pure function, no I/O).

    Postconditions:
      - returns "allow" when hasThoughts is false, or when consulted is true.
      - returns "block" only when hasThoughts is true and consulted is false.
    """
```

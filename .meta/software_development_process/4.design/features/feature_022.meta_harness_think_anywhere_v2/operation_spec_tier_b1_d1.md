# Operation Spec: Think Anywhere V2 — Tier B1+D1 modified operations

> Operation specifications for feature_022.meta_harness_think_anywhere_v2 — `omt_agent_guide.md §10`.
> Only operations whose contracts CHANGE are specified here (deltas vs Tier A spec).
> Unchanged: `omt_think_list`, `omt_think_remove`, `thinkGateDecision`, `hasConsultedThoughts`,
> `fileThoughtsIn`, digest, think-gate before-hook.

## `omt_think(path, thought, line?, after?, symbol?, category?) -> str` (modified)

```python
def omt_think(path, thought, line=None, after=None, symbol=None, category=None) -> str:
    """
    Operation: insert a language-aware TA: thought-tag inline in a non-protected file,
    addressed by raw line (back-compat), literal anchor, or symbol definition.      # B1

    Preconditions:
      - Tier A preconditions unchanged (exists, not protected, not .json, mapped ext).
      - AT MOST ONE of line / after / symbol is provided.                          # B1

    Exceptions (deny strings; no write occurs):
      - Tier A denials unchanged (protected / .json / missing / unknown ext /
        string-context / duplicate).
      - two or more addressing modes: deny naming the combination.                 # B1
      - after: literal substring matches 0 lines → "anchor not found" deny.        # B1
      - after/symbol: >1 lines match → deny naming count + up to 5 candidate
        line numbers (forces drift-resistant anchors).                             # B1
      - symbol: extension without a definition-pattern family (not .py, not JS/TS)
        → deny pointing at after:.                                                 # B1
      - symbol: name is regex-escaped before matching (metachars are literal).     # B1

    Postconditions:
      - exactly one TA: line inserted AFTER the uniquely resolved anchor line
        (after/symbol) or after `line` / at EOF (unchanged modes).                 # B1
      - resolved insertion point passes the A3 string-context guard (anchor mode
        composes with the triple-quote/fence refusal).                             # B1+A3
      - thoughts.jsonl record gains anchor: {kind:"after"|"symbol", value} for
        anchor modes, anchor:null for line/EOF mode (consumed later by E1).        # B1
      - returns "✅ TA: … → <path>:<line>" (unchanged shape).
    """
```

## `"tool.execute.after"` hook — read branch (enforcer; new behavior)

```python
def tool_execute_after(input, output) -> None:
    """
    Operation (new branch, runs before the edit-tools early return): on the FIRST
    read of a thought-carrying file per session, append the file's TA: thoughts
    to the read result — non-blocking, point-of-use delivery.                      # D1

    Preconditions:
      - input.tool == "read"; output.args carries a string filePath/path/file.
      - session state: Map<sessionID|"", Set<absPath>> inside the plugin closure.

    Exceptions: none — this branch never throws (fail-open via safeLog).

    Postconditions:
      - thought-free file / repeat read same session / non-read tool → output
        untouched.                                                                 # D1
      - first read with thoughts → output.output gains a trailing block:
        header naming the file + count + "think-gate applies; omt_think_list
        records consult", up to 10 "  <rel>:<line>: <content>" lines, then a
        "… (+M more)" pointer when truncated.                                      # D1
      - NO think_consult ledger record is written (awareness ≠ consult; the
        think-gate still blocks edits until omt_think_list).                       # D1
      - edit-path behavior (MVC++ lint, TDD revert, think-gate) is unchanged.
    """
```

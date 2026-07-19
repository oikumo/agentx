# Operation Spec: Meta Harness Improvement — modified hook operations

> Operation specifications for feature_023.meta_harness_improvement — `omt_agent_guide.md §10`.
> Only operations whose contracts CHANGE are specified here. Unchanged: all `omt_*` tools,
> `tool.execute.before`, think-gate decision helpers, `thinkDigest` content format,
> `navReminderMsg` content format.
>
> **Contract basis (pinned by T2.1):** installed `@opencode-ai/plugin@1.17.11` —
> `"tool.execute.after": (input: {tool; sessionID; callID; args}, output: {title; output;
> metadata})`. Runtime-verified against the opencode 1.18.3 binary call sites
> (`trigger("tool.execute.after", {tool,sessionID,callID,args}, {title,metadata,output})`).
> The feature_022 B1+D1 spec's "output.args carries filePath" precondition was WRONG — this
> spec supersedes it.

## `"tool.execute.after"` hook — read branch (enforcer; MODIFIED arg source, F14)

```python
def tool_execute_after_read_branch(input, output) -> None:
    """
    Operation: on the FIRST read of a thought-carrying file per session, append the
    file's TA: thoughts to the read result (D1 — unchanged INTENT, corrected arg source).

    Preconditions:
      - input.tool == "read".
      - input.args (NOT output.args — output NEVER carries args per the pinned
        contract) holds a string filePath / path / file.                          # F14 fix

    Exceptions: none — fail-open via safeLog (unchanged).

    Postconditions:
      - identical to the feature_022 D1 spec (once per file per session, 10-line
        cap, "… (+M more)" pointer, NO think_consult record, think-gate still
        blocks edits until omt_think_list) — but now actually reachable in
        production.                                                               # F14 fix
    """
```

## `"tool.execute.after"` hook — edit branch (enforcer; MODIFIED arg source, F14b)

```python
def tool_execute_after_edit_branch(input, output) -> None:
    """
    Operation: after an edit-tool call on a src/**/*.py file, block edits that
    introduced NEW mvc_check hard errors (vs the before-hook snapshot) and notify
    on warnings (feature_006 doctrine — live for the first time).

    Preconditions:
      - input.tool ∈ {"edit", "write", "patch", "multiedit"} (EDIT_TOOLS).
      - input.args holds a string filePath / path / file.                         # F14b fix
      - resolved rel is under src/ and ends with .py (else: no-op, unchanged).
      - hardSnapshot[abs] holds the pre-edit error counts captured by the
        before-hook (empty when no before-hook ran → every error is "introduced").

    Exceptions:
      - throws OmtBlock listing each introduced hard violation (rule, file:line,
        message) — the file was written; the agent corrects forward.              # now reachable
      - mvc_check failure → warn-log + snapshot cleanup, no throw (fail-open, unchanged).

    Postconditions:
      - introduced hard errors → OmtBlock; otherwise output untouched, warnings
        (≤3 shown) sent via notify (client-null-safe).                            # now reachable
    """
```

## `"tool.execute.after"` hook — session-first emission (BOTH plugins; NEW behavior, F14c)

```python
def tool_execute_after_session_first(input, output) -> None:
    """
    Operation: deliver the per-session digest/reminder on the FIRST dispatched
    tool.execute.after of each session — the live replacement for the never-
    dispatched session.start hook.                                               # F14c fix

    Preconditions:
      - any tool, any args; session key = input.sessionID or "".
      - omt_think.ts: module-level Set<session> (plugin has no per-session state
        today); omt_enforcer.ts: closure Set<session> beside injectedThisSession.

    Exceptions: none — fail-open; a digest failure never breaks the tool result.

    Postconditions:
      - first call of a session → output.output gains a trailing block:
        omt_think → thinkDigest() (30-line cap + stale count, format unchanged);
        omt_enforcer → navReminderMsg() (content unchanged).
      - subsequent calls same session → untouched (once-per-session, same
        discipline as D1's once-per-file).
      - session.start registrations RETAINED in both plugins (inert under
        opencode ≤1.18.3 per binary audit; live again if a future SDK dispatches
        the hook) — double delivery then is benign (digest is idempotent text).
    """
```

## Guard/test operations (no production contract change)

- `tests/scripts/omt/test_opencode_sdk_contract.py` — pins the d.ts shapes quoted above,
  the package==installed version, and the `_read_call` fixture arg placement. Fails loudly
  on SDK upgrade drift (the DEFECT-A → F14 lesson, mechanized).
- `_plugin_surface_runner.mjs` (new, modes `hooks` / `exports`) — read-only introspection of
  the real plugins; no state, no writes beyond stdout.
- `_think_gate_runner.mjs` gains `after-hook-edit` mode (canned mvc findings injected via a
  per-batch $ stub) — test-only surface, no plugin change.

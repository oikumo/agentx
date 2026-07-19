# Operation Spec: Think Anywhere V2 — Tier C new/modified operations

> Operation specifications for feature_022.meta_harness_think_anywhere_v2 — `omt_agent_guide.md §10`.
> Only operations whose contracts CHANGE are specified here (deltas vs Tier B1+D1 spec).
> Unchanged: `omt_think`, `omt_think_remove`, `thinkGateDecision`, `fileThoughtsIn`,
> D1 read-injection branch, nav/phase/skip tools.

## `omt_think_verify(path, line) -> str` (NEW)

```python
def omt_think_verify(path, line) -> str:
    """
    Operation: re-check a TA: thought's PLACEMENT INTEGRITY against the current
    file and record the outcome — the v2 feedback loop (verified/stale).        # C1
    Structural check only: existence at `line` plus, when an index add-record
    carries a B1 anchor, re-resolution of that anchor. Never judges semantic
    truth (agent's job at consult time).

    Preconditions:
      - path required; line required (1-based).
      - file exists; path not protected (.env*, README.md, uv.lock, LICENSE).
      - lines[line-1] matches THOUGHT_PATTERN (anchored comment-opener pattern).

    Exceptions (deny strings; no index write occurs):
      - missing path/line; protected path; missing file.
      - line out of range → denial naming the file's line count.
      - line is not a TA: comment (prose mention included) → "not a TA: comment".

    Postconditions:
      - index lookup: latest ADD-record (no `kind` field) for (path,line), else
        latest ADD-record for (path, thought-text) [drift fallback; latest wins].
      - record carries anchor → status = "verified" iff the anchor re-resolves
        uniquely AND resolved insert position == line, else "stale"
        (basis "anchor"; reason: not-found / ambiguous / moved).
      - no record or anchor:null → status "verified", basis "exists"
        (weaker: existence only; the message says so).
      - appends {ts, kind:"verify", path, line, category, thought, status,
        basis} to thoughts.jsonl (append-only; latest per (path,line) wins).
      - returns "✅ TA: verified — <rel>:<line> (basis: …)"
        or "⚠️ TA: STALE — <rel>:<line> — <reason>. Re-place with omt_think
        or remove with omt_think_remove."
      - reconcileIndex (omt_think_remove) already drops verify records for the
        removed slot — no zombie verify state (unchanged behavior, asserted).
    """
```

## `omt_think_list(path?, category?, query?) -> str` (modified)

```python
def omt_think_list(path=None, category=None, query=None) -> str:
    """
    Operation: grep-backed thought retrieval + CONSULT RECORDING (unchanged
    retrieval semantics; consult record gains per-file granularity).            # C2

    Preconditions / Exceptions: unchanged from Tier A.

    Postconditions:
      - rendered listing unchanged (50-cap, counts, pointer).
      - ALWAYS appends a think_consult ledger record — now with the consulted
        file set: {ts, kind:"think_consult", session,
                   files: sorted-unique rel paths of all grep hits (≤200),
                   files_truncated: true  # only when >200 hits' files }.       # C2
      - empty result → files: [] (covers nothing; no clearance granted).
    """
```

## `hasConsultedThoughts(session, rel?, opts?) -> bool` (modified, enforcer)

```python
def hasConsultedThoughts(session, rel=None, opts=None) -> bool:
    """
    Operation: decide whether the session has consulted thoughts FOR rel.       # C2

    Preconditions:
      - opts = {risk?: bool, root?: string}; root defaults process.cwd()
        (production call site passes the plugin `directory` — identical live).
      - rel omitted → whole-consult semantics identical to v1 (back-compat).

    Postconditions:
      - covered(record): rel omitted → true; record without `files` (legacy)
        → true (grandfathered, ages out with the window); else rel ∈ files.
      - exact-session consult covering rel → True.
      - else, cross-session consult within UNLOCK_WINDOW_MS covering rel →
        True ONLY IF NOT opts.risk (window dropped for risk:-carrying files).   # C2
      - otherwise False.
    """
```

## `thinkGateMsg(rel, thoughts, opts?) -> str` (modified, enforcer, module-local)

```python
def thinkGateMsg(rel, thoughts, opts=None) -> str:
    """
    Operation: render the think-gate block message — now WEIGHTED.              # C1

    Postconditions:
      - stable-sorted so risk:-category thoughts render first (category from
        /TA:\\s*([a-z0-9_-]+):/i — category position only, never text matches).
      - a thought line gains the suffix "  ⚠️ STALE" when opts.staleLines
        contains its line number (latest verify record status == "stale").
      - 10-line cap + "+M more" pointer unchanged; no-index → no markers
        (fail-open).
    """
```

## `thinkDigest() -> str` (modified, omt_think.ts session.start)

```python
def thinkDigest() -> str:
    """
    Postconditions (delta only):
      - reads thoughts.jsonl (fail-open); when current grep hits include
        thoughts whose latest verify record is "stale", the header gains:
        " ⚠️ N stale — re-check with omt_think_verify{path, line}."             # C1
      - 0-stale case renders exactly as Tier B1+D1 (no extra line).
    """
```

## think-gate call site (tool.execute.before — wiring delta)

```python
    thinkHits = fileThoughtsIn(abs)
    if thinkHits:
        risk = any(re.search(r"TA:\s*risk:", t.content, re.I) for t in thinkHits)
        consulted = hasConsultedThoughts(session, rel, {"risk": risk, "root": directory})
        if thinkGateDecision({"hasThoughts": True, "consulted": consulted}) == "block":
            raise OmtBlock(thinkGateMsg(rel, thinkHits,
                                        {"staleLines": staleLinesFor(directory, rel)}))
    # staleLinesFor(root, rel): latest verify records for path==rel whose status
    # is "stale" → Set of line numbers; fail-open empty.                        # C1+C2
```

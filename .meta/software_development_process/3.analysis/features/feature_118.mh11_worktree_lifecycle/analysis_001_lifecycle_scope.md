# Analysis 001 — worktree lifecycle scope (feature_118)

## Reproducer (gap)
MH11 d1–d3 ran sidecar worktrees by hand (.sandbox/bench/bugfix-*, resume-*, cross-*, harness-*; pinned, cleaned up): wall median 11.0%, tokens 0.0% structural, setup contention baked in. Manual discipline does not scale: nothing binds claim→branch, nothing refuses complete-without-commit, nothing checks net↔git drift. Improvement003 shipped the git-plane derived view (probe carries worktrees/branches/dirty/head; claim reserves feat/{task_id}; invariant triple-checks) but no lifecycle mutates it yet.

## Oracle (what passes)
1. claim(task_id) with gen-fenced generation creates .sandbox/bench/{task_id} on branch feat/{task_id} bound to the claim; double-claim refuses; unknown-task refuses.
2. fire(work_complete) refuses when: sidecar dirty vs HEAD (uncommitted work), no sidecar commit since claim, suite/check red, or expected_revision stale. Refusal is atomic (no partial merge, no ledger complete record).
3. Join merges locally and removes the worktree+branch; main protected (receipt guard + PROTECT-equivalent: join refuses on dirty main); every mutation appends ledger evidence (claim SHA, commit SHA, merge SHA, wall/tokens like bench transcripts).
4. Live harness green throughout (check 0 + build OK + e2e + suite + KNOWN empty; budgets held; Tier-3 excludes net; uv only; src/agentx/ untouched — D1 still locked).

## Budget (D3 gate)
- Analysis: this doc only (non-gated docs; no src/tests edits).
- Design: 1 design doc (claim/fire/join threading points + golden list + F7-hold rationale).
- Programming: receipt-disciplined rounds (ONE edit per file per e2e receipt; e2e file receipt-exempt); canary-gated goldens for new tests (omt_skip scope:tests); TDD auto-on (major_feature) — testlist → red → green → refactor → done at same test_node.
- Measurement: reuse bench/cli.py transcripts (tokens_est=io_bytes//4 confirmed); pre-warmed worktrees + cached uv sync to remove setup pole before claiming wall payback.

## Decisions needed (approval gate, no auto-fix)
- D1 join strategy: (a) --no-ff merge [RECOMMENDED: preserves sidecar evidence, matches ledger claim→complete chain] vs (b) --ff-only linear vs (c) squash.
- D2 capacity: HOLD F7 lane-only fan-out ≤2 [RECOMMENDED: B works inside the O4 lock; no new F7 reversal] vs extend standing parallel capacity (needs new decision + contention evidence).
- D3 root: reuse @var.git_worktree_root .sandbox/bench [RECOMMENDED: wild-pilot precedent, vars already shipped, no new root] vs new .worktrees/ dir.
- D4 conflict ownership: join refuses on conflict, owner resolves in sidecar [RECOMMENDED] vs auto-resolve.

## Non-goals
- No remote git (DENY unchanged). No D1 revisit (src/agentx/ untouched). No new gate (10/12 held) and no new op (closed enum unchanged) — lifecycle threads through existing claim/fire/gate/invariant.

    # Improvement 003 — Git-plane projection (local git + Petri-net global state)

Date: 2026-09-20. Workflow: meta_harness_evolution (fresh start, token-min first, DSL-first).
Trigger: git permission expanded (local git fully usable, remote still denied) + more freedom usable via net global state.
Selection: user picked A (git-plane projection) via approval gate 2026-09-20.

## Why this direction
- DENY stays: push/pull/fetch/ls-remote/remote/clone/submodule denied; local git (branch/worktree/status/log/diff/stash/commit) is the new freedom.
- MH11 wild pilots d1-d3 ran sidecar worktrees manually (.sandbox/bench/*, disjoint files, cleaned up): wall median 11.0%, tokens 0.0% structural, below O6a 15%/10% and O6b 25%/15%. Manual discipline does not scale; making git a derived view of the net removes the side channel.
- Probe rev 60 drained_complete enabled [] shows the net is SSOT but git-blind: worker_slots 2, agent_attention 1 (F7 serial), src/tests capacity 1 each. More git freedom without net binding = desync risk.

## Options considered
- A (SELECTED): git-plane as derived view — probe exposes {worktrees,branches,dirty,head}; claim reserves branch feat/{task_id} (gen-fenced); fire needs expected_revision; invariant triple-checks net↔ledger↔git. No new gate (10/12 held), closed op enum unchanged, no new tool args.
- B: worktree-per-claim runtime (claim creates worktree, complete needs sidecar commit+green, join merges locally). Deferred: needs F7 full reversal + join semantics; A is its read-only prerequisite.
- C: ledger-commit evidence bind (complete pins SHA, audit/mine read history). Deferred: needs A's branch naming + triple drift first.
- D: read-only advisory only. Rejected as under-powered: same probe cost, no claim/fire binding, desync remains possible.

## DSL change (this iteration, .meta/META_HARNESS.omt only)
- VAR: git_worktree_root=.sandbox/bench, git_branch_prefix=feat/ (wild-pilot precedent, vars not prose).
- PRED: none added (closed vocab HDL-1; TS owns builtins) — git-plane folded into net_marking description.
- GATE g.net: + git-plane triple-drift note (fail-closed unchanged, order 35 unchanged).
- STATE: git_plane derived view (git worktree list + branch + status --porcelain, live local-only; sidecars only, main protected; revert via worktree remove --force + branch -D).
- DOC git.plane (GIT_PLANE): local lifecycle in sidecars only, remote stays denied, main via user commit/join; probe/claim/fire/invariant contract.
- TOOL omt_net: payload + git-plane derived view (no new op, no new args; branch=prefix+task_id naming only).
- BUDGET: tool_schemas 1856->1920 (+64 deliberate), nav_index 65536->66560 (+1024 deliberate) in same edit (diet headroom was 9B/16B).
- TS seed: .opencode/plugins/omt_net.ts irToolDescription synced byte-exact (376B -> 450B).

## Verification
- harnessc check 274 records 0 errors (was 270; +vars/state/doc, no new gate/pred/tool).
- e2e + build follow; projections regenerated, never hand-edited.
- Next (not this iteration): B (worktree lifecycle) needs F7 decision + join spec; C needs ledger SHA pin; O6 bridge still needs D1 revisit.

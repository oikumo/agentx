# Design 001 — worktree lifecycle threading (feature_118)

Locked decisions (user-approved 2026-09-20): join --no-ff · hold fan-out ≤2 (F7 lane lock, no new reversal) · root .sandbox/bench (reuse @var.git_worktree_root).

## 1. Landscape (what exists)
- workspace.py (081): worktree-per-generation lane — branch omt/{task}/g{gen}, dir .worktrees/{task}-g{gen}/, metadata-authoritative FAIL-OPEN (missing git never blocks claim; generation fence is the security property). No import of state (state imports it).
- dispatch_runtime.py (114): pure plan composer — Task{claim,task_id,lane,worktree,lease} with LOGICAL worktree names wt-{batch}-{task}; caller state.dispatch_claims validates at live rev and commits claims+join atomically. Fan-out ≤2, WIP cap 15, lanes 0/1.
- claim_task / dispatch_claims / fire(work_complete) in state.py: _require_revision stale guard + _transact lock authority; join does work_complete per task restoring worker slots.
- Bench pilots d1–d3: manual sidecars under .sandbox/bench/* with feat-agnostic names; evidence shape wall/tokens/io/verify/success + transcripts.

## 2. Reconciliation (two lanes, one contract)
B does NOT rewrite the 081 lane. It adds an MH11 session lane with lane-scoped naming, sharing refusal-code shape and fence semantics:
- 081 lane (managed plane): root .worktrees/, branch omt/{task}/g{gen} — unchanged, default for claim_task without lane override.
- B lane (session plane): root @var.git_worktree_root (.sandbox/bench/), branch @var.git_branch_prefix+{task_id}-g{gen} (feat/T-g3 keeps 080 gen-fencing + 042 template compat) — selected by lane=general + session-plane flag in the claim envelope.
- Shared: generation fence on every publish path; containment via is_path_in_workspace; unknown/dup/stale refusals stay stable.

## 3. New module: worktree_lifecycle.py (pure + thin git boundary)
- resolve_lane(task_id, generation, lane) -> {root, branch, path}: pure, golden-pinned (no FS).
- status_checks(path, branch, base_commit) -> {clean, branch_exists, commit_since_claim, head}: thin subprocess boundary (git status --porcelain, rev-parse --verify, rev-list base..head --count); all failures fail CLOSED to {clean:False} (B inverts 081 fail-open at the complete-gate only — claim stays fail-open like 081).
- compose_join(tasks, base_branch='main') -> {commands:[merge --no-ff, worktree remove --force, branch -D], digests}: pure command composer; caller executes (no subprocess inside composer — testable, golden-pinned).
- Refusal codes (stable, pre-write): unclean_sidecar | no_commit_since_claim | unknown_workspace | main_dirty | join_conflict | worker_capacity_exhausted (reuse 114) | stale_revision (reuse _require_revision).

## 4. Threading points (receipt-disciplined, one edit per file per round)
1. state.claim_task envelope += workspace binding via workspace.build_workspace with lane override (B lane when task came from session-plane claim); ledger records {path,branch,base_commit}.
2. state.dispatch_claims plan tasks: logical wt-* names gain real path/branch for B-lane tasks (plan_to_dict += {path,branch}); preview (probe plan[]) shows binding without creating FS.
3. Creation (ensure) stays best-effort at claim (081 semantics preserved); the FAIL-CLOSED gate lives at fire(work_complete)/join: status_checks must pass + caller passes verify evidence (suite green); join refuses on main_dirty or conflict (owner resolves in sidecar per D4).
4. cli.py: claim/create + join subcommands thread expected_revision through (existing flags); join emits merge --no-ff then cleanup; ledger batch carrier holds commit SHAs (C follow-up consumes).
5. invariant: triple-drift net↔ledger↔git (improvement003 text) gains teeth — unknown_workspace / branch-missing / base-mismatch surface as drift, not silent.

## 5. Goldens (canary-gated, tests/scripts/omt/test_net_worktree_lifecycle_b.py)
- resolve_lane determinism (both lanes, gen fencing in branch names).
- compose_join shape (--no-ff present, remove+delete present, order pinned).
- Refusals: unclean_sidecar / no_commit_since_claim / unknown_workspace / main_dirty / join_conflict (hermetic tmp git repos; no live-repo mutation).
- Regression: 081 lane unchanged (omt/ prefix + .worktrees/ still resolve).
- Target: 8 goldens; full suite + check 0 + e2e per round.

## 6. F7-hold rationale
Fan-out ≤2 held: planner caps (WORKER_SLOTS_CAP=2, lane 0/1, WIP 15) untouched; B only makes the ≤2 slots REAL (sidecar isolation + commit evidence) instead of logical. Standing capacity needs new contention data (d1 verify -45.7% contention note) — explicitly out of scope.

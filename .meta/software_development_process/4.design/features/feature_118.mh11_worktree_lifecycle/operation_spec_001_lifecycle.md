# Operation Spec 001 — feature_118.mh11_worktree_lifecycle: public operation contracts

> Phase: Design companion to design_001. Each operation: signature, pre, post/effects, errors. Net engine (state firing, _transact, _require_revision) UNCHANGED — lifecycle reuses claim envelope / dispatch join / fire_marking exactly; no new places/transitions; no new ledger kind. Fan-out ≤2 held (F7 lane lock).

## scripts/omt/net/worktree_lifecycle.py — pure composer + thin git boundary (design §3)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| resolve_lane(task_id, generation, lane) | task_id non-empty, generation ≥ 0, lane in general (B session lane) or managed (081 lane) | Deterministic lane binding: B lane gives root .sandbox/bench and branch feat/T-gN; managed lane gives root .worktrees and branch omt/T-gN. Pure, stdlib-only, no I/O. | unknown_task on empty task_id; bad_generation on negative generation |
| status_checks(path, branch, base_commit) | path/branch/base_commit from resolve_lane plus claim binding | Closed reading via git status, rev-parse, rev-list: clean flag, branch_exists, commits_since_claim, head SHA. Thin boundary; every subprocess failure fails CLOSED to clean False. | none raised — callers map to refusals |
| compose_join(tasks, base main) | tasks are B-lane bound tasks with path/branch/head | Pure command plan: merge --no-ff per branch (ordered by task_id), then worktree remove --force plus branch -D per task, plus digests. No subprocess — caller executes. | empty_join on no tasks; unknown_workspace on task missing path/branch |
| gate_complete(status, verify_ok, expected_rev, live_rev) | status from status_checks; verify_ok is caller suite-green evidence; revisions from menu/live | Returns None when clean plus branch_exists plus commits_since_claim ≥ 1 plus verify_ok plus revision match. | unclean_sidecar, no_commit_since_claim, unknown_workspace, verify_red, stale_revision |

## scripts/omt/net/state.py — lifecycle threading (design §4)

| Op | Pre | Post / effects | Errors |
|---|---|---|---|
| claim_task with lane workspace | claim envelope plus resolve_lane binding | Ledger net_claim gains workspace id/path/branch/base_commit; creation best-effort (081 fail-open preserved at claim). | Existing claim refusals unchanged (unknown_task, dup, stale) |
| dispatch_claims with B-lane paths | plan from preview at R | plan_to_dict tasks gain path/branch for B-lane tasks; preview stays read-only (no FS). | Planner refuse codes unchanged |
| fire work_complete plus join | gate_complete passes for every B-lane task; main clean | Atomic join: per-task work_complete (slots restored) plus merge record; zero partial marks on any refuse. | unclean_sidecar, no_commit_since_claim, main_dirty, join_conflict (plus existing stale) |

## scripts/omt/net/cli.py — lifecycle CLI (design §4)

| Op | Contract |
|---|---|
| claim --task T --lane session | Prints claim envelope including workspace path/branch/base_commit; expected-revision stale guard (existing flag). |
| join --expected-revision R --dry-run | Dry-run prints compose_join commands only; commit path executes merge --no-ff per task then cleanup; refuses on main_dirty/conflict (owner resolves in sidecar); errors use ok-false envelope, exit 2. |

## tests/scripts/omt/test_net_worktree_lifecycle_b.py — pytest suite (design §5)

| Op | Contract |
|---|---|
| resolve vectors | B lane resolves under .sandbox/bench with feat prefix; managed lane under .worktrees with omt prefix (081 regression) |
| compose vectors | --no-ff present per task, ordered by task_id; worktree remove plus branch -D follow each merge |
| refusal vectors | unclean / no-commit / unknown-workspace / main-dirty / join-conflict (hermetic tmp git repos; live rev 60 untouched) |
| isolation vectors | hermetic OMT_NET_DIR / OMT_LEDGER_PATH tmp per test; no net places/transitions added (Tier-3) |

## Global invariants

- **Net structure untouched** — no splice in lifecycle; place_invariants hold.
- **Ledger kinds reused only** — net_claim / net_fire (plus workspace annotation, no new kind).
- **F7 held** — worker cap 2, lanes 0/1, WIP 15 untouched; src/agentx untouched (D1); uv only.

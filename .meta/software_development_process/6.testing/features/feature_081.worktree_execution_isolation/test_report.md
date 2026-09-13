# Test report — feature_081.worktree_execution_isolation (T5-3 2C)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `worktree_execution_isolation` (mh8 T5-3, strict slice order, D11, NEXT_STEP
  §7–§9): one claim = one generation = one branch (`omt/<task>/g<gen>`) = one
  worktree (`.worktrees/<task>-g<gen>/`). New `scripts/omt/net/workspace.py`
  (pure path/metadata helpers, no `state` import — no cycle); `claim_task` /
  `transfer_task` stamp `workspace:{id,path,branch,base_commit}` and
  best-effort bootstrap the dir (+ git branch when available, fail-open);
  `checkpoint_task` records `head_commit` / `patch_digest` into the workspace
  on result submission; `check_workspace_edit` containment gate
  (`workspace_mismatch` — a claim never authorizes the integration worktree,
  plus `stale_generation` / `not_owner` / `task_not_active` fencing);
  `gate.check_managed_edit_allowed` wrapper (legacy solo path untouched, D8)
  wired into CLI `gate --task-id --generation --owner`; claim/transfer
  envelopes carry the `task.workspace` block (additive); plugin `OP_ARGS`
  gate gains the three already-described args (no new schema, no budget move,
  no `.omt` change). Workers run with `OMT_NET_DIR` + `OMT_COORDINATION_ROOT`
  at the shared bundle (coordinator bootstrap contract, §7.1).

## Goldens (`tests/scripts/omt/test_net_worktree_isolation.py`, 7 green)

- Claim stamps workspace: `T1-g1` / `omt/T1/g1` / `.worktrees/T1-g1` /
  `base_commit` str; worktree dir exists on disk (claim IS the bootstrap).
- Two worktrees dirty independently, one authority: T1+T2 claimed, distinct
  dirs hold distinct dirty files, both bindings observable at one revision.
- Integration refused, workspace allowed: `check_workspace_edit` OK inside
  the generation's dir, `workspace_mismatch` for the repo integration path.
- Wrong owner (`not_owner`) and wrong generation (`stale_generation`) refuse.
- Transfer → new workspace: gen 2 gets `T1-g2` (+ dir), old `T1-g1` dir
  survives on disk but gen-1 checkpoint refuses `stale_generation`.
- Checkpoint records `head_commit` / `patch_digest` into the workspace.
- CLI round-trip: `gate --task-id T1 --generation 1 --owner alice` allows the
  workspace path (rc 0), refuses the integration path (rc 1).

## Incidental discipline notes

- Genuine RED (7 failed, `KeyError: 'workspace'`) → GREEN after the staged
  batch; one RED-side fix (keyword-only `generation=`/`path=` at two call
  sites — implementation signature mirrors `claim_task` style, tests adapted).
- One malformed generated line (missing open-quote, `state.py:960`) fixed
  inside the staged batch before the boundary e2e — stage bypass covers
  intra-batch fixes; single e2e still validates the final patch (D-bar).
- Shipped-test pin update (080 `TestCliRoundTrip`, exact `task` dict): the
  additive `workspace` key is the deliberate 081 bootstrap contract (080's
  own rationale — worker learns generation without a follow-up probe —
  extends to path/branch); rewritten as key-access with all 080 values
  intact + `workspace.id` pin. Canary re-issued (`skip-latest-wins`: the
  Programming declaration shadowed the first skip) immediately before edit.
- `stage-vs-policy_ver`: 6 files staged
  (`state/cli/gate/workspace/plugin` + new goldens), one boundary e2e.
- Budgets UNCHANGED (tool_args 2454/2464, tool_schemas 1812/1856): gate
  task-scoping reuses the already-described `task_id`/`owner`/`generation`
  args; `.omt` `@tool omt_net` args already list them — description untouched.
- Deferred with rationale (strict slice order): `worker_slots=2` capacity +
  component-aware scope conflicts + third-task refusal + probe menu → T5-4
  2D; real `git worktree add` linkage (dir+branch record now, best-effort
  branch) + verification/integration lane → 3A; journal/recovery → 3B.

## Verification

- New goldens: 7/7 green.
- Related: claim/authority/cli/plugin-args/isolation — 40/40 green.
- Boundary e2e (`test_omt_harness_e2e.py`): 1/1 green (post-all-edits).
- `harnessc check`: 0 errors (263 records; only the pre-existing
  `self_evaluation.md` drift warning, untouched) · `build`: OK (5 projections).
- Full suite: 2113 passed, 0 failed.

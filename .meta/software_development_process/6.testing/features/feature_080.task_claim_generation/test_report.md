# Test report — feature_080.task_claim_generation (T5-2 2B)

> Date: 2026-09-13 · Type: minor_feature · Status: PASS

## Scope verified

- `task_claim_generation` (mh8 T5-2, strict slice order, D9/D10/D14): slice-1
  named bindings (feature_064, observation-only, generation recorded-not-enforced)
  become enforceable ownership — `claim_task` / `release_task` /
  `transfer_task` / `checkpoint_task` in `scripts/omt/net/state.py`, all via
  the T5-1 `_transact` authority (lock + `expected_revision` + `command_id`),
  plus `claim|release|transfer|checkpoint` CLI ops and the `omt_net` plugin
  whitelist. Revision stays the short CAS token; per-task generation is the
  long ownership fence (an unrelated rev bump never revokes a held generation).

## Goldens (`tests/scripts/omt/test_net_task_claim_generation.py`, 10 green)

- Same-task race (2 forked procs, barrier-synced, rev 0): exactly 1 commit
  (gen 1, winner recorded) + 1 `stale_revision` — the in-lock authoritative
  revision check refuses the loser before the binding check (D10 for the claim
  path). A re-claim at the fresh rev refuses `task_not_pending` (pinned
  sequentially).
- Unrelated rev bump keeps generation: claim gen 1 → 2 unrelated splices
  (rev 1→3) → gen-1 checkpoint still submits (rev 4, D9).
- Stale generation cannot submit: transfer gen 1→2, old-gen checkpoint
  refuses `stale_generation`, new-gen submits; release keeps gen, reclaim
  bumps (gen 2), old-gen refuses.
- Refusals: unknown task `task_not_found` (no write); double claim
  `task_not_pending`; wrong-owner release `not_owner`; release clears owner
  and returns binding + tokens to pending.
- Idempotency (D14): same `command_id` + same claim replays with no rev bump;
  same ID + different op → `command_id_conflict`, no write.
- CLI round-trip: `claim` envelope carries the post-commit `task`
  block (id/place/owner/generation); `checkpoint --mutation` JSON evidence;
  malformed JSON → `invalid_mutation` exit 1.

## Incidental discipline notes

- `skip-latest-wins` (canary, scope: tests): new hermetic goldens only.
- Race-loser code: first RED pinned `task_not_pending`, live behavior is
  `stale_revision` (revision gate precedes the binding gate inside `_transact`);
  corrected after RED — the stable code for same-rev losers, `task_not_pending`
  reserved for fresh-rev double claims.
- `stage-vs-budgets`: `harnessc stage` refuses outside a staged session for
  policy files; budgets raised deliberately in the same pass instead
  (tool_args 2400→2464, tool_schemas 1792→1856; measured 2454/1812), 059 pins
  re-measured (NAV_INDEX 63963, TOOL_ARGS 2454, TOOL_SCHEMAS 1812) per 078
  precedent. New plugin schema args kept to three (`task_id`, `owner`,
  `generation`); `command_id` stays CLI-only (fire precedent); checkpoint
  evidence reuses `mutation`.
- Deferred with rationale (strict slice order): capacity/scope arbitration
  (worker_slots, scope conflicts) belongs to T5-4 2D; worktree-scoped managed
  gates (incl. refusing unbound `fire(work_start)`) belong to 2C/2D — claim
  is the task-aware `work_start` they build on. No token moves beyond the
  work_pending↔work_active pair (resource arbitration untouched).

## Verification

- New goldens: 10/10 green.
- Related: net claim/authority/plugin-args/059-pins/harnessc/e2e — 60/60 green.
- Full suite: `tests/` 954 passed; features+scripts+automated 1675 passed with
  3 pre-existing TUI e2e failures, stash-verified at clean HEAD (environmental,
  same class as 077's live-timeout pin).
- `harnessc check`: 0 errors (263 records) · `build`: OK (5 projections).

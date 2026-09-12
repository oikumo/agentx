# Design 001 — named bindings + truthful observation (feature_064, slice 1)

Status: accepted (D4). Scope: observation only — no claims, no integration.

## 1. Binding schema (sidecar `task_bindings`, revision-coupled)

```json
{"id": "agentx-retrieval-progress",
 "objective": "AgentX retrieval progress in UI",
 "acceptance_refs": ["controller/partner event contract v3"],
 "deps": [{"need": "event contract", "satisfied_by": "contract v3"}],
 "place": "work_pending | work_active | work_done",
 "owner": "" | "coordinator" | "worker-a" | "worker-b",
 "generation": 0,
 "checkpoint": "",
 "scope": ["src/agentx/retrieval/"],
 "resources": ["worker_slot"],
 "results": [],
 "block_reason": ""}
```

Required: non-empty string `id`, `place` in pool places. Optional fields keep
their zero values; types are checked lightly (lists stay lists, strings stay
strings). `generation` is recorded, not enforced — atomic compare-and-update
is slice 2.

## 2. Placement — why the sidecar

The overlay is RE-DERIVED at every `save()` (P10); extra overlay keys would be
wiped (only `disabled` is preserved). The sidecar already carries live state
with atomic three-file save + revision coupling, so `task_bindings` rides the
same transaction: `load()` reads `sidecar.get("task_bindings", [])` (fail-open
on missing/legacy bundles), `save()` persists it. No fourth file, no new op
(closed `omt_net` enum untouched — the TS whitelist mirror gotcha does not
trigger).

## 3. Validation (`validate_task_bindings`)

- Must be a list; every entry a dict; unique non-empty `id`s; `place` in pool
  places; `owner` a string (empty = unclaimed, still ≤1 owner by schema).
- Per-place report: `{bindings, tokens, anonymous = tokens - bindings}`.
  `anonymous >= 0` required — bindings are a named subset of live tokens, so
  the pre-existing `work_done=7` bundle validates with 7 anonymous dones
  (no auto-backfill — D4-style caution: never mutate user data silently).
- `consistent` = zero errors. `load()` never raises on bindings; the probe
  surfaces `bindings_valid` + errors (fail-open observation, fail-closed
  enforcement stays with the gates).

## 4. Probe observation/menu (additive keys only)

- `observation`: `{state, reason, revision, basis}`. States: `inconsistent`
  (validation errors) > `executing` (active>0) > `awaiting_capacity`
  (pending>0, `work_start` disabled + which resource/attention blocks) >
  `drained_complete` (pending=active=0, done>0) > `idle_empty` (all zero).
  `basis` = `"live_marking rev N"` for marking/menu; analyzer output labeled
  `"initial-marking analysis (<=max_states states)"` — never a live claim.
- `menu`: `{next, other_enabled, blocked, resources}` mirroring the WORK.md
  order; task-bound actions (`implement <id>`, `verify <id>`, `resume <id>`)
  from bindings, transition names as fallback when no bindings exist.
- `tasks`: the validated bindings + per-place coverage. Existing envelope keys
  (`marking`, `enabled`, `advice`) are byte-identical.

## 5. Explicitly deferred (slices 2–3)

Slice 2: write path (`bindings` op or equivalent with TS mirror + atomic
claim: expected-revision + readiness + owner + capacity + scope-conflict check,
generation fencing). Slice 3: checkpoints/transfer/recovery, serialized
integration, objective-level acceptance. No task reaches Done on self-report —
that invariant is specified here, enforced there.

## 6. Invariants under test

Bindings⊆tokens per place; ≤1 owner per task; counts survive save/load;
empty-legacy bundles load; same observation inputs → same state/reason;
analyzer labels present; no existing envelope key changes shape.

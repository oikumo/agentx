# Test report — feature_119.ledger_backed_fix_preview

First linked feature of `agentx_concurrent_development` (origin: scaffold).
Replaces the improvement005 static `fix_preview` map with live data:
`foldProjectDrift()` + WORK.md stamped `net_rev` + `headSha()`, read-only.

## Goldens: tests/scripts/omt/test_omt_q.py::TestOpFixPreview — 6/6

- unlinked-project-backed → rev-pinned `link` line + `project.py link` apply cmd with `expected_revision`.
- aging-draft (28d relative fixture, no absolute dates) → SKIP + `apply: nothing linkable`.
- filter `aging` keeps framing + matching class, drops `unlinked-project-backed`.
- clean ledger → `preview rev:60 (0 drift records)` + `- clean`.
- read-only: ledger bytes byte-identical across the probe call.
- live shape smoke (`use_real_root`): HEAD-sha envelope, `preview rev:` framing, list preview.

## Targeted runs

- test_omt_q.py: 26/26 green (20 pre-existing + 6 new).
- Neighbors (same plugin surface): test_omt_q_audit, test_omt_q_state_summary,
  test_project_lifecycle — 30/30 green.
- harnessc check 275/0; build 5 projections; e2e 1 passed.
- Live bun probe: 18 drift records mapped (2 link groups + 2 aging + 5 iter-log
  SKIPs), `filter:unlinked` subset correct.

## Notes

- tests/ canary via omt_skip{scope:tests} (logged); receipt round-robin held:
  one edit per harness file per round, e2e refresh between rounds (the
  assertion-fix second edit waited for a fresh receipt).
- LSP `subprocess.run([BUN, ...])` Optional-arg error at test_omt_q.py:900 is
  pre-existing HEAD code (hql probe), not this feature — left untouched.
- No TDD auto-on (minor_feature); no new gate (10/12); budgets fit
  (tool_args 2536/2592, tool_schemas 1871/2048, nav_index 66136/66560).

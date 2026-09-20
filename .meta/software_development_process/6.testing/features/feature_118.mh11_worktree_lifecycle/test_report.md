# Test report - feature_118.mh11_worktree_lifecycle (B worktree lifecycle)

## Goldens: tests/scripts/omt/test_net_worktree_lifecycle_b.py - 11/11
Cycle 1 composer (9): resolve session lane bench+feat+gN; managed lane
081 regression; empty-task/bad-generation refusals; compose --no-ff ordered
with remove+-D cleanup; empty/unknown-workspace refusals; gate pass
(clean+commit+verify+rev); gate refusals (unclean/no-commit/red/stale);
status closed-on-git-error; status reads real tmp repo.
Cycle 2 threading (2): dispatch stamps session sidecar (binding + report
+ ledger net_claim branch feat/t-1-g1); preview carries sidecar with no FS
side effects (live repo untouched).

## Targeted runs
- B file: 11/11 green.
- Neighbors (shape-regression guard): test_net_dispatch_o4,
  test_net_worktree_isolation, test_net_task_claim_generation,
  test_net_cli - all green (workspace additive sidecar key breaks nothing;
  dispatch worktree/ledger batch asserts byte-identical).
- harnessc check 274/0; test_harnessc 34/34; e2e 1 passed.

## Full suite
1887 passed + 2 deselected; 2 failed, both pre-existing at the 118
Programming baseline (improvement003 deliberate budget growth, unrelated):
test_budget_pins::test_tight_budgets_unchanged,
test_budget_diet::test_live_check_emits_diet_warnings.
Self-caused transient: stray repo-root 5.implementation dir tripped
root_allowlist (2 harnessc failures); moved to the canonical
software_development_process path and re-greened - see impl_notes. No new failures vs baseline.

## TDD
testlist(8 behaviors) - red(C1 composer node) - green - sync -
red(C2 threading node) - green - sync - done. Same-node red/green both
cycles. TDD auto-on (major_feature). omt_tdd sync clean, done approved.

## Contract honored
--no-ff join, fan-out <=2 held, .sandbox/bench reused (user D1-D3);
D4 join refuses on conflict. F7/D1 untouched. uv only.

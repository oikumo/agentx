# Operation Spec 001 — feature_132 pilot launch-path: guarded pre-checks (no launches)

> Phase: Design companion to `design_001_pilot_launch_path.md` (promotes 131/design_004). All ops stdlib-only, **no OpenCode launches, no tokens**; every refusal is a named finding, never silent. Real execution stays `no_safe_launch` until all pre-checks pass + explicit `p` invocation + resource claims.

## `run_gate.py` (new, planned) — pre-execution gates

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `check_manifest(mdoc) -> ok` | manifest dict v1 with experiment/run/cases/variants/reps | `validate()` passes, `expand_matrix()` yields 12 trials for run_001 | `Finding(manifest_invalid, {missing|reason})` |
| `check_isolation(mdoc, *, base=/tmp) -> ok` | per-trial worktree/selector planned, no repo writes outside allowlist | isolation paths exist-or-creatable under base, protected dests refused | `Finding(isolation_unavailable, {dest|reason})` |
| `check_budgets(mdoc, *, budgets) -> ok` | tokens/time/concurrency bounds pinned | bounds present + non-zero, overhead tracked separately | `Finding(budget_missing, {field})` |
| `check_claims(*, net_available) -> ok` | `omt_net` dispatch/claim controls reachable | claims held for 12 trials, no second scheduler minted | `Finding(no_safe_launch, {reason: claims_unavailable})` |
| `gate_run(mdoc, *, isolation, budgets, claims, explicit_p) -> decision` | all above + `explicit_p is True` | `{allowed: True, n_trials: 12}` only if every check ok; else `{allowed: False, reason}` | `no_safe_launch` | `manifest_invalid` | `isolation_unavailable` | `budget_missing` — `executed` always False in Design slice |

## `service.py` / `evaluate.py` (existing, unchanged this slice)

| Op | Pre | Post |
|---|---|---|
| `experiment dry_run` | valid manifest | 12 trials + label lines, `executed: False` |
| `experiment run` | any manifest | `{ok: False, reason: no_safe_launch, executed: False}` until gate_run allows (future slice) |

## Test hooks (synthetic only)

- Fixture manifests (valid/invalid), fake isolation base under `/tmp`, stubbed claims — never touch live DB or launch OpenCode.

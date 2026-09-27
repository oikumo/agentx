# Operation Spec 001 — feature_134 fake-executor launcher (no live runs)

> Design companion to `design_001_real_trial_launcher.md` (DECIDED). All ops stdlib-only, fake executor only; `executed` stays False for fakes (live `executed:true` is a future slice). Every failure is a named finding.

## `launcher.py` (new, planned fake core)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `plan_trials(mdoc) -> list` | valid manifest v1 | 12-trial matrix via `expand_matrix`, order-seed shuffle recorded | `Finding(manifest_invalid)` |
| `dispatch_fake(trial, *, executor) -> FakeResult` | trial from plan, fake executor injected | executor called once with trial + isolation (`/tmp` per-trial stub); returns `{trial, outcome, usage_stub, attempt:1}`; no threads, concurrency 1 | `Finding(dispatch_failed, {trial})` on executor exception |
| `enforce_timeout(result, *, budget_s=300) -> result` | fake duration supplied | duration ≤300 → pass through; over → `{outcome: timeout_failed}` (strict-once, no retry) | — |
| `collect_fake(results, *, manifest) -> TrialReport stub` | 12 fake results | per-trial membership + stub usage + findings; usable = outcome pass; independent N = usable count | propagates `manifest_invalid` |
| `run_fake(mdoc, *, executor, claims, explicit_p) -> decision` | 132 `gate_run` allowed + claims held 12 + explicit_p | `{allowed:True, n_trials:12, executed:False, fake_n:12}` (fakes prove wiring, never live) | gate refusal → same `no_safe_launch` mapping as 133 dispatcher |

## Invariants (fake slice)

- Executor is injected fake (records calls, returns canned outcomes); no subprocess, no tokens, no sleeps.
- Concurrency 1 (sequential loop); `/tmp` paths stubbed, never created outside `tmp_path`.
- Strict-once: timeout produces failed trial, never a second attempt.

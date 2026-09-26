# Discharge Design — feature_130 (sandbox only)

Source: `discharge_analysis.md` (data source verified live, matrix, task specs, arm methods) + `stage_real_tokens_design.md`/`run_real_tokens.py` (feature_129 seam + `--ledger` + threshold-on-measured-tokens, digest `40e6ab74b10b038a` — UNCHANGED by this feature) + proposal §§14.2/14.3/15.6.
Rule: sandbox only; stdlib only; advisory boundary; no src/tests/net/ledger/toolbox change; `run_real_tokens.py` is not modified (discharge is a data change, not a design change).

## 1. Label spec (exact)

- First line of every capture prompt, byte-exact: `[harness_reason:discharge arm=<arm> case=<case>]` with `<arm> ∈ {harness, planner, kernel}` and `<case> ∈ {H1, H3}` (closed sets; 6 valid labels).
- The Task-tool short `description` carries the same marker (it echoes into the session title → checkable after the fact without trusting titles alone).
- Grammar (harvest regex): `^\[harness_reason:discharge arm=(harness|planner|kernel) case=(H1|H3)\]`.
- Uniqueness: exactly one labeled session per valid label. Any duplicate, extra, or mismatched label → harvest fails loudly (no silent pick, no synthetic fill).

## 2. Session matrix + spawn protocol

| # | arm | case | batch/slot | scratch dir |
|---|-----|------|------------|-------------|
| 1 | harness | H1 | 1/0 | `/tmp/opencode/discharge_harness_H1/` |
| 2 | planner | H1 | 1/1 | `/tmp/opencode/discharge_planner_H1/` |
| 3 | kernel | H1 | 1/2 | `/tmp/opencode/discharge_kernel_H1/` |
| 4 | kernel | H3 | 2/0 (rotated) | `/tmp/opencode/discharge_kernel_H3/` |
| 5 | planner | H3 | 2/1 | `/tmp/opencode/discharge_planner_H3/` |
| 6 | harness | H3 | 2/2 | `/tmp/opencode/discharge_harness_H3/` |

- Capture window: record `since_ms` (`time.time()*1000`, integer) immediately before spawning batch 1; harvest only considers sessions with `time_created >= since_ms`.
- Spawn: 3 concurrent Task-tool subagents per batch, slots in listed order; subagent type `general` for all (same type, same inherited model).
- Each prompt carries: label line (§1), the verbatim task text (§3, identical across arms per §14.2), the arm-method block (§3, the ONLY inter-arm difference), read-only repo discipline, unique scratch dir, "work naturally" instruction, "do not delegate to further subagents" (clean single-session attribution).
- Sessions must be COMPLETE (Task tool returned) before harvest; cumulative token columns are final then.

## 3. Full session prompts

Common wrapper (parameterized `ARM`, `CASE`, `SCRATCH`; everything outside the arm block is byte-identical across the 6 spawns):

```
[harness_reason:discharge arm=ARM case=CASE]

You are doing a measured cost-comparison task. Work naturally — neither artificially
brief nor padded; your session token usage is the measurand. Work ALONE: do not
delegate to further subagents. The repository is READ-ONLY for you: do not create,
modify, or delete any file inside it. All scratch work goes in SCRATCH (create it).
Run any Python with: uv run --no-sync python ...

TASK (CASE) — same text for all arms:
<H1 or H3 task text below, verbatim>

YOUR ARM'S METHOD — the only difference between arms, by design:
<harness | planner | kernel method text below>

DELIVERABLE (final message):
<H1 or H3 deliverable spec below>
```

**H1 task text (verbatim):** Reuse across two real contexts (R2 pattern). Re-instantiate the `verify_candidate` macro for two contexts: Ctx-A (artifact = content-digest of `.sandbox/harness_reason/stage0_contracts.json`) and Ctx-B (artifact = content-digest of `.sandbox/harness_reason/stage0_ir.json`). For each context produce a verdict + the fresh obligations it incurs. Demonstrate explicitly that Ctx-B (artifact h2) must NOT be verified with Ctx-A evidence (h1) — show where that refusal binds. Close with a reused-vs-fresh step accounting: what the macro/fragment/laws provided unchanged vs what had to be derived fresh per context.

**H3 task text (verbatim):** Interruption/resume with reuse (R3 pattern). Copy `.sandbox/harness_reason/` to `SCRATCH/resume_copy/`. Build a sha256 manifest (pre-interruption state) for these 4 named files: `stage0_contracts.json`, `stage0_ir.json`, `run_checker.py`, `run_composer.py`. Record one small derivation per file (content-digest → verdict or obligation). Then mutate exactly ONE of the 4 files (in the copy only). Resume: recompute digests; classify each file preserved (digest-equal → derivation reused) vs stale (re-import + re-derive); never combine pre-mutation derivations with post-mutation state (no mixed-epoch plan); count avoided steps (derivations reused without re-derivation).

**Arm method texts:**
- harness (A0): Use the existing harness discipline as-is — receipt/dependency-authority thinking: evidence is per-artifact, freshness is digest-match, stale inputs are re-imported. Read sandbox files as needed and produce the deliverable as a written report.
- planner (A1): FIRST write a conventional typed plan (signatures/templates + per-step obligations) into your scratch dir, THEN execute it step by step. Do not run kernel scripts (`run_checker.py`/`run_composer.py` machinery) — plan and execute manually.
- kernel (A2): Derive verdicts by calling the kernel ops (`run_composer.expand_verify_candidate` / `run_composer.rewrite` / `run_checker.make_cert` / `run_checker.explain`) via small driver scripts in your scratch dir run under `uv run --no-sync python`; read verdicts from certs/refusals.

**Deliverable specs:**
- H1: per-context verdicts (Ctx-A, Ctx-B) + fresh obligations listed; the h2-with-h1 refusal with its bind location; reused-vs-fresh step accounting.
- H3: pre-interruption manifest digests; the 4 derivations; which file was mutated; per-file resume classification (preserved/stale); avoided-steps count.

## 4. Harvester — `harvest_ledger.py` outline (stdlib only, read-only DB)

1. Args: `--since <ms>` (capture window) `--out <path>` (default `.sandbox/harness_reason/stage_real_tokens_ledger.json`). Open `~/.local/share/opencode/opencode.db` with sqlite URI `file:...?mode=ro` (read-only, never writes).
2. Candidate query (verified schema, 2026-09-26):
   `SELECT id, parent_id, directory, title, agent, model, time_created, time_updated, tokens_input, tokens_output, tokens_reasoning, tokens_cache_read, tokens_cache_write, cost FROM session WHERE parent_id IS NOT NULL AND directory = ? AND time_created >= ? ORDER BY time_created` (directory = this project's abs path).
3. Label verification per candidate (primary path `session_input.prompt`; fallback: first user `message`→`part` text; both probed live at implementation — pick the one that reproduces the known sample): first line must match the §1 grammar; extract `(arm, case)`.
4. Validation (fail = non-zero exit, no partial ledger write):
   - exactly 6 labeled sessions; exactly one per label; zero unlabeled/foreign-label candidates in window → else `harvest_label_conflict`.
   - every mapping key ∈ the 6 expected `<arm>:<case>`; unknown → `unknown(arm_or_case_outside_closed_set)`.
   - `prompt_tokens = tokens_input + tokens_cache_read`, `completion_tokens = tokens_output + tokens_reasoning` (disclosed mapping; both > 0, integers) → else `harvest_token_column_invalid`.
   - `latency_ms = (time_updated - time_created) * 1000` from the session row (real wall time, frozen at harvest; no fake precision).
   - synthetic numbers are never written: values come only from DB columns.
5. Write ledger (§5) with provenance; print 6/6 key summary + per-row totals.

## 5. Ledger schema (runner-compatible)

Top-level JSON object: 6 row keys `<arm>:<case>` + one `provenance` key. Runner lookups are `LEDGER[f"{arm}:{case}"]` over exactly the arm/case closed sets → `provenance` is never matched (ignored by the runner, by design — f129 design note).

```json
{
  "provenance": {
    "source": "opencode session DB (~/.local/share/opencode/opencode.db), read-only",
    "harvested_at": "<iso8601>", "capture_window_since_ms": <int>,
    "project_directory": "<abs path>",
    "mapping": "prompt_tokens = tokens_input + tokens_cache_read; completion_tokens = tokens_output + tokens_reasoning",
    "caveat": "one real session per (arm,case); runner replays each capture across R=3 reps (feature_129 documented caveat)"
  },
  "harness:H1": {"prompt_tokens": <int>, "completion_tokens": <int>, "latency_ms": <int>,
                 "session_id": "ses_...", "label": "[harness_reason:discharge arm=harness case=H1]",
                 "agent": "...", "model": "...", "time_created": <int>},
  "...": "6 rows total: harness:H1, planner:H1, kernel:H1, kernel:H3, planner:H3, harness:H3"
}
```

## 6. `--ledger` re-run procedure + expected honest outcome

1. `uv run --no-sync python .sandbox/harness_reason/harvest_ledger.py --since <ms>` → prints 6/6 + writes `stage_real_tokens_ledger.json`.
2. `uv run --no-sync python .sandbox/harness_reason/run_real_tokens.py --ledger` → 8/8 V-checks pass, `REAL_TOKENS_OK <digest>`; summary now: measured 18/135 (6 keys × R=3), `proxy: "mixed"` (T01–T12 + H2 unmeasured — honest), per-arm medians on measured rows, threshold `>=15%` reduction vs harness evaluated on measured medians, verdict `keep-kernel-candidate` or `shrink-tier0-or-keep-planner` (decision rule, not prediction).
3. Re-run step 2 (digest byte-stable across runs — ledger JSON fixed at harvest).
4. Unledgered run must still print `REAL_TOKENS_OK 40e6ab74b10b038a` (f129 baseline preserved — proof `run_real_tokens.py` unchanged).

## 7. Regression set (Testing phase)

S0 `run_probes.py` 7/7 (`6e355d71`) · S1 `run_checker.py` 12/12 · S2 `run_composer.py` 7/7 · S3 `run_experiment.py` 7/7 (`d476df80d71d829a`) · tier0 `tier0_demo.py` PASS · tier1 `tier1_demo.py` PASS + `tests/scripts/reason/` 14 · unledgered real-tokens digest `40e6ab74b10b038a` · ledged run 8/8 ×2 stable + threshold reading recorded.

## 8. Fairness + caveats (unchanged from analysis, restated for the gate)

Same task text verbatim / same model (inherited) / same subagent type / rotated spawn order; arms differ only in method block. One capture per (arm, case) replayed across R=3 — medians sit on 2 distinct real points per arm; `proxy` stays `mixed`; kernel arm drives sandbox kernel scripts (Tier-1 `reason_check` not exposed to subagents — that is the Tier-0/1 reality being measured); small pilot proves nothing universal.

## Next

Implement `harvest_ledger.py` (Programming) → record capture window → spawn batch 1 (H1 × 3 arms) + batch 2 (H3, rotated) → harvest → `--ledger` re-run → Testing (regression + digest ×2 + test report) → Done (PROJECT.md/CURRENT_STATE.md update).

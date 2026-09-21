# Round 002 — Package 1: filesystem containment (AXR-01, AXR-02, AXR-12 share)

> Workflow: `.workflows/agentx/loops/consistency_enforcement.md` (override — no OMT gates for this run; `omt_think` + mocked tests + approval gate still apply).
> Project: `agentx_1_0_0` (draft) — repair-only, order 1→6, acceptance = per-finding Regression check.
> Scope source: `sandbox/consistency_enforcement/round_001_implementation_review.md` (§AXR-01, §AXR-02, §AXR-12, §Repair sequence pkg 1) + probes `round_001_review_probes.py` (20/20 pass = defects reproduced, never CI gates).
> Step: strategy 3 (propose) — STOP at step 4 approval gate. No `src/` edits applied in this round.

## 1. Confirmed gaps (summary, not re-proof)

- **AXR-01** `src/agentx/model/coding/coding_tools.py:231-234` `_file_edit_impl`: target validated via `_resolve_safe_path`, but write goes to predictable `<file>.tmp` via `write_text` → pre-planted symlink followed, `replace` overwrites outside file. Boundary: needs writable outside file + pre-existing symlink; app-level, not OS-container escape.
- **AXR-02** same file `:123-138` `_file_search_impl`: start dir validated, each `rglob` result read unchecked (`is_file`/`read_text` follow symlinks); `relative_to` on lexical link path misses escape. `_file_read_impl("link.txt")` correctly rejects, search leaks first-5-lines context (reads whole file to build preview).
- **AXR-12** `src/agentx/utils/utils.py:97-130` `is_directory_allowed_to_deletion`: lexical `Path` compare, no `..` norm / symlink resolve; first `is_relative_to` result discarded; `relative_to` accepts `<cwd>/local_sessions/../unrelated`. Only predicate probed; `shutil.rmtree` not invoked; no `src/` call site found (latent API defect).
- Shared contract (PROJECT D5): AXR-01/02/12 share **one path policy** + explicit concurrent-rename threat bound.

## 2. Alternatives (pick one per group; recommended marked *)

### G1 — AXR-01 atomic edit
- **A1* — exclusive temp + atomic replace (report recipe).** `tempfile.mkstemp(dir=target_parent_validated)` → write via fd → `os.replace` → preserve perms → cleanup on fail. Never reuses predictable `.tmp`. Closes demonstrated pre-existing-symlink attack.
- **A2 — minimal guard.** Keep `.tmp` name but refuse if `.tmp` exists as symlink / non-regular file. Cheaper, leaves predictable-name + race surface; label partial.

### G2 — AXR-02 search containment
- **B1* — resolve+validate every result (report recipe).** For each `rglob` hit: `resolve()` → containment check vs sandbox root → read validated target, not link path. Same policy for read/list. Separately test in-sandbox symlink support.
- **B2 — exclude symlinks from search.** Skip `is_symlink()` hits entirely. Simpler, no target reads; changes product behaviour for legit in-sandbox links.

### G3 — shared policy + AXR-12 guard
- **C1* — one helper, three callers (D5).** Harden `_resolve_safe_path` (resolve + normalize + containment, return canonical) and reuse in search/read/list/edit/create; deletion guard resolves candidate + trusted allowed-roots, checks containment explicitly, deletes validated canonical path. Decide: allowed-roots may be symlinks? may root itself be deleted? Keep `PermissionError` contract. Document concurrent-rename bound (dir-handle-relative ops or explicit stable-ancestry bound, race unexercised).
- **C2 — local-only deletion fix.** Patch `is_directory_allowed_to_deletion` in place (resolve + check), leave coding tools on separate logic. Faster, duplicates policy; drift risk.

### Cross-cutting (applies to whichever combo)
- Preview bound: stop loading whole file to return 5 lines (cap read).
- Regression tests per finding's Regression check (AXR-01: pre-created `.tmp` symlink → outside unchanged + target regular; AXR-02: outside symlink excluded/rejected, regular + in-sandbox-link cases; AXR-12: reject traversal/outside-symlink/sibling-prefix, accept ordinary child, `PermissionError` preserved; guard-alone before any `rmtree` on disposable dirs).
- Probes retired, not gated (D4). Reconcile design examples + test assertions (coding File Edit / OP-5) with corrected behaviour.

## 3. Approval gate (step 4 — awaiting user)

Pick one per group, e.g. `A1+B1+C1` (recommended full containment) or variants.
Reply with a single letter from the menu in the agent message. No `src/` edits until go-ahead (step 5). Results go to `# Result` below after execution (step 6).

## 4. Execution notes (for step 5, after approval)

- Mocked unit tests first (rule 3); sub-agents for parallel analysis where useful (rule 4).
- `omt_think` embeds knowledge in touched source (rule 2, invariant).
- Record per finding: repaired revision, test nodes/commands, coverage, residual limits (concurrent-rename bound, symlink policy).

# Result (executed 2026-09-20 — user said "do all" → combo A A1+B1+C1)

- **Chosen:** A (full containment). `src/agentx/model/coding/coding_tools.py`: `mkstemp(dir=parent)` O_EXCL + `os.replace`, perm preserve, cleanup; search resolves+validates every `rglob` result, reads validated target, 5-line preview cap (no whole-file load). `src/agentx/utils/utils.py`: canonical resolve + explicit `relative_to` containment for candidate + allowed roots, `PermissionError` contract kept, `dangerous_delete_directory` removes validated canonical path. `omt_think` added in both files.
- **Observation probes (must stop passing):** `uv run pytest -q sandbox/consistency_enforcement/round_001_review_probes.py -k "axr01 or axr02 or axr12"` → **3 failed** (faulty no longer reproduced): `test_axr01_predictable_temp_symlink`, `test_axr02_search_reads_outside_symlink`, `test_axr12_guard_accepts_traversal_and_symlink`. Signal only, not proof.
- **Regression proof (this session, disposable dirs):** AXR-01 pre-planted `.tmp` symlink → outside unchanged + target regular with new content PASS; AXR-02 outside symlink excluded from context + `inner.txt` still found PASS; AXR-12 ordinary child accept + traversal/sibling-prefix reject (`PermissionError`) PASS.
- **Existing suite:** `uv run pytest -q tests/ -k "coding or utils or deletion or file_search or file_edit"` → **91 passed**.
- **Residuals:** concurrent-rename race bound to stable ancestry (unexercised, same as report); allowed-root itself deletable (preserved contract, recorded decision); `_file_list_impl` name-only, no content leak fix applied.
- **Next:** Packages 2–6 still open (provider, policy, session, RAG, conversation+recovery). Do not close Package 1 until durable regression tests land in `tests/` (canary approval needed). CLOSED 2026-09-20: 5 durable tests landed in `tests/features/feature_019.coding_agent_screen/test_axr01_axr02_axr12_filesystem_containment.py` (canary).

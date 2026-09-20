# Proposal: split the test suite by ownership and test level

Status: proposal only; no tests have been moved.

## Decision proposed

Replace the mixed `tests/` tree with two independently discoverable test roots:

```text
tests_meta_harness/
├── unit/
├── functional/
└── end_to_end/

test_agentx/
├── unit/
├── functional/
└── end_to_end/
```

This proposal preserves the requested names exactly, including the intentional
`tests_meta_harness` / `test_agentx` singular-plural asymmetry. If symmetric
naming is preferred, decide that before implementation; renaming a root during
the migration would create unnecessary path churn.

The split has two independent dimensions:

1. **Ownership** chooses the root: META harness or AgentX application.
2. **Test level** chooses the required subfolder: unit, functional, or
   end-to-end.

A feature number, current directory, or test filename must not decide either
dimension by itself. The system under test and the boundary crossed by the test
are the deciding facts.

## Why this refactor is needed

The current `tests/` tree contains 153 tracked-or-working-tree Python files
matching `test_*.py`, distributed across several incompatible organizational
schemes:

| Current top-level area | Test-file count | Main concern |
|---|---:|---|
| `tests/features/` | 72 | AgentX and META-harness features are mixed |
| `tests/scripts/` | 68 | Primarily OMT/META-harness tests, but organized by source path |
| `tests/model/` | 5 | AgentX model tests with unclear level |
| `tests/controllers/` | 3 | AgentX component/interaction tests |
| `tests/unit/` | 3 | Level is explicit, ownership is not |
| `tests/views/` | 2 | AgentX view tests |

The tree also contains runtime or generated material such as `__pycache__/`,
`tests/local_sessions/current/agent_session.db`, and `tests/test_sandbox/`.
Those items need an explicit fixture/artifact decision rather than being moved
blindly into a new test root.

The main migration risk is not pytest discovery. META-harness policy currently
recognizes `tests/` as a privileged path in multiple locations. Moving files
without first teaching the enforcement and TDD layers about both new roots
would silently weaken the tests-canary and two-hats protections.

## Classification rules

### Ownership

Put a test in `tests_meta_harness/` when its primary subject is one or more of:

- `.meta/META_HARNESS.omt`, generated harness artifacts, or OMT policy;
- `scripts/omt/` tooling;
- `.opencode/plugins/omt_*` or `.opencode/lib/enforcer/` behavior;
- work/net/project lifecycle, phase, TDD, receipt, navigation, KB-gate, or
  concurrency policy owned by the META harness.

Put a test in `test_agentx/` when its primary subject is one or more of:

- production code under `src/agentx/`;
- AgentX models, controllers, views, persistence, providers, commands, RAG, or
  user-facing behavior;
- an application feature whose acceptance behavior is delivered by AgentX.

For a genuinely cross-domain test, ownership belongs to the entry point being
verified. A test that invokes OMT to validate an AgentX workflow is META-owned;
a test that runs AgentX while using an OMT helper only as test infrastructure is
AgentX-owned. Do not duplicate the same test in both roots.

### Test level

| Level | Definition | Allowed boundaries | Typical duration |
|---|---|---|---|
| `unit` | Verifies one function, class, module, or policy rule in isolation | In-memory collaborators; mocks/fakes; temporary values | Fast |
| `functional` | Verifies a feature or multi-component use case through a stable internal interface | Temporary filesystem or database; multiple real components; no live external service | Moderate |
| `end_to_end` | Verifies a complete user/tool workflow through its real entry point | CLI/subprocess, generated artifacts, full harness cycle, or explicitly marked live provider | Slowest |

Directory level is authoritative. Pytest markers may mirror the level for
selection, but markers must not contradict the directory.

### Initial mapping from the current tree

This is a starting point for the migration manifest, not permission to move a
whole directory without reviewing individual tests.

| Current area | Proposed destination | Notes |
|---|---|---|
| `tests/scripts/omt/` | `tests_meta_harness/{unit,functional,end_to_end}/` | Classify each file by boundary; `test_omt_harness_e2e.py` is explicitly end-to-end |
| Harness-owned directories under `tests/features/` | `tests_meta_harness/functional/<feature>/` by default | Unit-level policy tests may go to `unit/`; full CLI/session paths go to `end_to_end/` |
| AgentX-owned directories under `tests/features/` | `test_agentx/functional/<feature>/` by default | Preserve feature slug as the subdirectory |
| `tests/model/`, `tests/controllers/`, `tests/views/` | `test_agentx/unit/<component>/` or `functional/<component>/` | Decide from actual collaborators, not the current folder name |
| `tests/unit/` | Usually `test_agentx/unit/` | Re-evaluate any harness-owned test |
| `tests/conftest.py`, `tests/testing_utils.py`, `tests/constants.py` | Root-local support modules | Split by ownership; duplicate only tiny immutable constants when that prevents cross-root coupling |
| `tests/test_sandbox/`, `tests/local_sessions/` | Fixture directory under the owning test, or `.sandbox/` runtime output | Never collect mutable runtime state as a test module |

## Target conventions

Each root must always contain all three required level folders, even if one is
temporarily empty during migration. Suggested full shape:

```text
tests_meta_harness/
├── conftest.py
├── unit/
│   ├── enforcer/
│   ├── net/
│   └── tdd/
├── functional/
│   ├── features/
│   ├── kb/
│   └── project_lifecycle/
└── end_to_end/
    ├── harness/
    └── live/

test_agentx/
├── conftest.py
├── unit/
│   ├── controllers/
│   ├── model/
│   ├── persistence/
│   └── views/
├── functional/
│   └── features/
└── end_to_end/
    ├── cli/
    └── providers/
```

Rules for the target tree:

- Use unique test-module basenames where practical. If duplicate basenames are
  needed, enable and validate pytest's importlib import mode before the moves.
- Add `__init__.py` only where package semantics or relative imports require
  it; do not add it mechanically to every directory.
- Keep fixtures in the narrowest `conftest.py` that serves them.
- Do not import fixtures from the other ownership root.
- Live-provider tests remain explicitly marked (currently `opencode_live`) and
  excluded by the default test command.
- Generated databases, caches, and session outputs must use temporary
  directories and must not be committed under either root.

## Migration procedure

### Phase 0 — approve scope and capture the baseline

1. Confirm the two root names and this classification policy.
2. Start from a clean, dedicated migration branch or worktree. Do not mix the
   moves with behavior changes.
3. Record the current file inventory and collection result:

   ```bash
   git status --short
   git ls-files tests > /tmp/agentx-tests-files-before.txt
   uv run pytest --collect-only -q > /tmp/agentx-tests-collect-before.txt
   uv run pytest -q
   ```

4. Record pass/fail/skip/deselect totals and the names of any expected failures.
   The present structural baseline is 153 `test_*.py` files; the collected test
   count must be taken from the command because one file can contain many test
   nodes.
5. Create a migration manifest with one row per tracked test/support file and
   these columns:

   ```text
   source | owner | level | destination | fixture_dependencies | path_consumers | status | rationale
   ```

No move begins until every test file has an owner, level, and destination.

### Phase 1 — make policy recognize the future roots

Do this before creating or editing tests in the new roots.

1. Replace single-path `tests/` assumptions with a shared definition equivalent
   to `TEST_ROOTS = ("tests_meta_harness/", "test_agentx/")`. During the
   transition, include legacy `tests/` as a third recognized root.
2. Apply that definition consistently to:

   - tests-canary detection and receipt guards;
   - TDD two-hats path classification;
   - net permission/gate checks;
   - feature-scoped test-directory resolution;
   - preflight messages and generated AGENTS instructions;
   - harness E2E receipt constants and commands;
   - scaffolding defaults and benchmark fixture paths.

3. Known path-sensitive surfaces observed in the repository include:

   - `.meta/META_HARNESS.omt` and `scripts/omt/harnessc.py`;
   - `.opencode/lib/omt_shared.ts`;
   - `.opencode/lib/enforcer/{gate_driver,receipt_guard,phase_gate,tdd_hats,preflight,task_prep}.ts`;
   - `scripts/omt/tdd/{gates,state,cli}.py` and `scripts/omt/new_feature.py`;
   - `.opencode/plugins/omt_q.ts` and benchmark task definitions;
   - KB lesson/evidence paths and source comments that pin exact test files.

4. Consolidate harness-surface edits into the fewest safe rounds because a
   fresh E2E receipt is required between protected harness edits.
5. Add tests proving that both new roots are gated exactly like legacy `tests/`,
   and that unrelated paths are not misclassified.
6. Rebuild generated harness artifacts from their source; never hand-edit
   generated `AGENTS.md`.

Exit condition: a preflight probe against a synthetic path in each new root
fires the same tests-canary/TDD rules as the equivalent legacy path.

### Phase 2 — create the roots and establish dual discovery

1. Create all six required level directories.
2. Temporarily configure pytest to discover all three roots:

   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests", "tests_meta_harness", "test_agentx"]
   pythonpath = ["src"]
   ```

3. Add the markers `unit`, `functional`, and `end_to_end` only if marker-based
   selection is useful. Directory placement remains mandatory.
4. Run collection and confirm that empty new roots introduce no errors or
   duplicate nodes.

Exit condition: the baseline suite still collects and runs unchanged while the
new roots are protected by the harness.

### Phase 3 — split fixtures and support code

1. Inventory which tests consume every fixture/helper in the current root
   `conftest.py`, `testing_utils.py`, and `constants.py`.
2. Move AgentX-only helpers into `test_agentx/`; move META-only helpers into
   `tests_meta_harness/`.
3. For genuinely generic helpers, prefer a small installed/importable support
   module with no domain dependencies over importing across test roots.
4. Convert mutable filesystem/database fixtures to `tmp_path` or another
   per-test temporary location.
5. Run collection and the affected batch after every fixture split.

Exit condition: neither root imports test support from the other root or from
legacy `tests/`.

### Phase 4 — move META-harness tests in small batches

Use `git mv` so history remains easy to follow. Recommended order:

1. Pure policy/parser/unit tests to `tests_meta_harness/unit/`.
2. Multi-component OMT and feature tests to
   `tests_meta_harness/functional/`.
3. Harness CLI, live process, worktree, and full-cycle tests to
   `tests_meta_harness/end_to_end/`.
4. Update exact path constants, golden references, KB evidence links, source
   comments, and commands in the same batch as their test.
5. For every batch, compare collection IDs and run:

   ```bash
   uv run pytest tests_meta_harness/unit -q
   uv run pytest tests_meta_harness/functional -q
   uv run pytest tests_meta_harness/end_to_end -q
   uv run pytest -q
   ```

Exit condition: all META-harness-owned tests have moved and no harness source or
tooling references their old paths.

### Phase 5 — move AgentX tests in small batches

Recommended order:

1. Existing isolated tests to `test_agentx/unit/` by component.
2. Controller/model/view tests after checking whether they are truly unit or
   functional.
3. AgentX feature acceptance tests to `test_agentx/functional/features/`.
4. CLI, full session, and live-provider journeys to
   `test_agentx/end_to_end/`.
5. Preserve feature directory slugs when they carry traceability value.
6. After each batch, run the moved directory and then the full default suite:

   ```bash
   uv run pytest test_agentx/unit -q
   uv run pytest test_agentx/functional -q
   uv run pytest test_agentx/end_to_end -q
   uv run pytest -q
   ```

Exit condition: every application-owned test is under `test_agentx/`, and no
test depends on legacy-root import behavior.

### Phase 6 — switch discovery and remove the compatibility root

1. Confirm the manifest has no `pending` rows.
2. Change pytest configuration to the final roots:

   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests_meta_harness", "test_agentx"]
   pythonpath = ["src"]
   ```

3. Remove legacy `tests/` from the shared gate/path definition.
4. Remove the legacy directory only after proving that it contains no tracked
   or required fixture files. Do not leave symlinks: pytest may double-collect
   tests through them.
5. Update commands in CI, developer tooling, OMT recipes, benchmarks, and
   documentation.
6. Regenerate the final collection list:

   ```bash
   uv run pytest tests_meta_harness test_agentx --collect-only -q > /tmp/agentx-tests-collect-after.txt
   uv run pytest -q
   uv run pytest -m opencode_live -q
   ```

   Run the live marker only in an environment where its external dependencies
   and execution budget are available; otherwise record it as an explicit
   deferred validation rather than silently treating it as passed.

### Phase 7 — final audit

1. Compare before/after node IDs semantically. Paths will change, so normalize
   root prefixes before diffing. Every removed node must be intentionally
   renamed, consolidated, or documented.
2. Search for stale `tests/` references and classify every match as historical,
   generated, fixture data, or a missed executable reference.
3. Confirm both new roots are covered by tests-canary, TDD, net gate, and
   scaffolding behavior.
4. Confirm no caches, databases, local sessions, or run outputs are tracked in
   either root.
5. Run the harness compiler checks and the complete default test suite.
6. Record results, exceptions, and deferred live checks in the migration
   artifact.

## Validation matrix

| Validation | META harness | AgentX | Whole repository |
|---|---|---|---|
| Collect only | Each of 3 level dirs | Each of 3 level dirs | Both roots together |
| Focused tests | Changed/moved batch | Changed/moved batch | N/A |
| Default suite | Root alone | Root alone | `uv run pytest -q` |
| Live/E2E | Harness full-cycle receipt | Marked provider/CLI journeys | Explicit scheduled run |
| Gate behavior | Canary + TDD + net paths | Canary + TDD + net paths | Generated policy agrees |
| Reference audit | OMT/tool paths | app commands/docs | No executable legacy paths |

## Acceptance criteria

The refactor is complete only when all of the following are true:

- `tests_meta_harness/` and `test_agentx/` each contain `unit/`, `functional/`,
  and `end_to_end/`.
- Legacy `tests/` no longer exists and no compatibility symlink remains.
- Every pre-migration test node has a documented post-migration equivalent or
  an approved removal rationale.
- Default collection and execution have no duplicate-module/import errors.
- Default pass/fail/skip/deselect results match the baseline except for approved
  changes.
- Editing a test under either new root triggers the same tests-canary and TDD
  protections that previously applied to `tests/`.
- The harness E2E receipt command points to its new end-to-end location and
  passes.
- No executable code, CI job, benchmark, KB evidence item, or generated policy
  still depends on an obsolete `tests/` path.
- Runtime artifacts and caches are absent from both test roots.
- The full repository suite passes with `uv run pytest -q`.

## Rollback procedure

Perform the implementation in reviewable batches. If a batch changes
collection unexpectedly or fails tests:

1. Stop moving additional files.
2. Reverse only that batch's `git mv` operations and its paired path-reference
   edits; do not use a broad destructive reset.
3. Restore the transitional three-root `testpaths` configuration.
4. Run the baseline collection and default suite again.
5. Correct the manifest classification or fixture dependency before retrying.

The old `tests/` root remains a valid fallback until Phase 6. After Phase 6,
rollback should restore the last reviewed migration batch rather than recreate
the entire tree manually.

## Explicit non-goals

- Rewriting test behavior while relocating files.
- Converting all functional tests into unit tests.
- Changing production behavior under `src/agentx/`.
- Merging META-harness and AgentX fixtures for convenience.
- Removing slow/live tests merely to improve suite time.
- Executing this proposal without a separate approval and implementation task.

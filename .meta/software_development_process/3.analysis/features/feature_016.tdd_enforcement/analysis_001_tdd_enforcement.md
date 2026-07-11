# Analysis — feature_016: TDD Enforcement

> Spec source: `.meta/doc/tdd/tdd-agent-spec.md` (Kent Beck TDD, v5, agent-exec)
> Architecture constraint: `omt_enforcer.ts` is a MUST — the Python script is called BY the enforcer, not instead of it.

---

## 1. Problem Statement

The OMT++ Programming phase is unstructured. An agent can write all production code
first, bolt on tests afterward, and pass the phase-exit check (which only verifies
that test files exist). Nothing enforces Kent Beck's TDD cycle (Red → Green → Refactor)
or the three laws:

- L1: No production code without a failing test
- L2: Test is minimal-to-fail
- L3: Production code is minimal-to-pass

The existing gate (`omt_enforcer.ts`) enforces phase progression and MVC++ architecture
but has no TDD state machine. A separate Python script (`tdd_check.py`) can provide
AST-based analysis that TypeScript cannot, following the proven `mvc_check.py` pattern.

---

## 2. Use Case: TDD-Driven Feature Implementation

**Actor:** AI coding agent (opencode session)

**Preconditions:**
- Agent has declared `omt_phase{task_type:"major_feature", phase:"Programming", tdd:true}`
- Design artifacts exist (phase gate already verified)

**Main flow:**
1. Agent calls `omt_testlist{behaviors:[...]}` → records behaviors to implement
2. Agent writes a test file (tests/ allowed in RED state)
3. Agent calls `omt_red{test_node}` → script runs pytest (must fail), AST-verifies true RED
4. Agent calls `omt_green{test_node}` → script runs pytest (must pass), saves AST snapshot
5. Agent calls `omt_refactor{test_node}` → script runs pytest (must stay green)
6. Agent edits src/ during GREEN/REFACTOR (tests/ blocked — two hats principle)
7. Repeat 2-6 until test list empty
8. Agent calls `omt_done{feature}` → full checklist verification

**Alternative flows:**
- Agent tries to edit src/ during RED → BLOCKED (test hat only)
- Agent tries to edit tests/ during GREEN → BLOCKED (code hat only)
- REFACTOR breaks tests → edit auto-reverted
- Agent calls `omt_skip{reason:"..."}` → override (logged)

---

## 3. Analysis Class Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    omt_enforcer.ts                       │
│  (TypeScript — the GATE, stays as-is + thin TDD wrappers)│
│                                                          │
│  omt_testlist ─┐                                        │
│  omt_red ──────┤── $`uv run scripts/omt/tdd_check.py`  │
│  omt_green ────┤        (delegates to Python)           │
│  omt_refactor ─┤                                        │
│  omt_done ─────┘                                        │
│                                                          │
│  tool.execute.before ── gate ── tdd_check.py gate       │
│  tool.execute.after ── advisory ── tdd_check.py after-edit│
│  omt_complete ── validate-exit ── tdd_check.py validate  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  scripts/omt/tdd_check.py                 │
│  (Python — the TDD ENGINE, stdlib only)                  │
│                                                          │
│  Subcommands:                                            │
│  ├── testlist    — record behaviors                      │
│  ├── start       — RED: pytest + AST (true RED check)    │
│  ├── green       — GREEN: pytest + AST (snapshot, L3)    │
│  ├── refactor    — REFACTOR: pytest + AST (no new behav) │
│  ├── done        — DONE: full checklist + coverage gaps  │
│  ├── gate        — ledger read → {allowed, reason}       │
│  ├── after-edit  — quick AST scan → advisories           │
│  ├── status      — TDD state + cycle history             │
│  ├── validate-exit — full AST scan → {ok, gaps}          │
│  └── revert      — git checkout / snapshot restore       │
│                                                          │
│  AST Functions:                                          │
│  ├── infer_target_src(test_file) → list[str]             │
│  ├── extract_test_references(test_file, test_name)       │
│  ├── extract_defined_names(src_file) → set[str]          │
│  ├── extract_public_methods(src_file) → list[dict]       │
│  ├── find_untested_methods(src, tests) → list[dict]      │
│  ├── verify_true_red(test, src) → {is_true_red, missing} │
│  ├── detect_anti_patterns(test, state) → list[str]       │
│  └── snapshot_source(src_file) → dict                    │
│                                                          │
│  Ledger: .meta/.omt/ledger.jsonl (shared with enforcer)  │
│  Snapshots: .meta/.omt/tdd_snapshots/ (gitignored)       │
└─────────────────────────────────────────────────────────┘
```

---

## 4. FSM States and Gate Rules

From the spec's "two hats" principle:

| State | src/ edits | tests/ edits | Hat | Spec reference |
|---|---|---|---|---|
| TESTLIST | BLOCKED | BLOCKED | Planning | spec FSM: "enumerate behaviors, no code" |
| RED | BLOCKED | ALLOWED | Test hat | spec L1: "no prod code without failing test" |
| GREEN | ALLOWED | BLOCKED | Code hat | spec L3: "prod=min-to-pass" |
| REFACTOR | ALLOWED | BLOCKED | Refactor hat | spec: "two_hats_never_same_time" |
| DONE | BLOCKED | BLOCKED | Complete | spec done_checklist |

Transitions:
- TESTLIST → RED: via `omt_testlist` then `omt_red`
- RED → GREEN: via `omt_green` (pytest must pass)
- GREEN → REFACTOR: via `omt_refactor` (pytest must stay green)
- GREEN/REFACTOR → RED: via `omt_red` (next behavior)
- REFACTOR → DONE: via `omt_done` (checklist verified)

---

## 5. AST Capabilities (Python-only)

| Capability | What it does | TDD law |
|---|---|---|
| Test→Target inference | Parse test imports → source file paths | L1 (test before code) |
| True RED verification | Test references methods not in source | L1 (failing = missing code) |
| Law 3 check | New src methods not referenced by test | L3 (min-to-pass) |
| Coverage gap analysis | Untested public methods at phase exit | done_checklist |
| Anti-pattern detection | batch-N-tests, skip/xfail, naming | spec anti-patterns |
| Source snapshot diff | New methods since last green | L3 enforcement |
| Test content extraction | Assertions + calls for teaching msgs | Philosophy (teach) |

---

## 6. Data Dictionary

| Entity | Location | Format |
|---|---|---|
| Ledger | `.meta/.omt/ledger.jsonl` | JSONL (shared with enforcer) |
| TDD record | Ledger | `{kind:"tdd", state, test_node, target_src, verified, exit_code, feature}` |
| Testlist record | Ledger | `{kind:"tdd_testlist", behaviors:[...], remaining:[...], feature}` |
| Snapshot | `.meta/.omt/tdd_snapshots/<file_stem>.json` | JSON (methods, line numbers) |
| Gate response | stdout JSON | `{allowed, reason, state, tdd_mode, warning?}` |
| RED response | stdout JSON | `{ok, state, verified, exit_code, message, is_true_red?, missing?, test_summary?}` |
| GREEN response | stdout JSON | `{ok, state, verified, exit_code, message, law3_violations?}` |
| DONE response | stdout JSON | `{ok, checklist:{...}, coverage_gaps:[...]}` |

---

## 7. NFRs

| ID | Requirement |
|---|---|
| P1 | Gate call (per src/ edit) < 100ms — ledger read only, no pytest, no AST |
| P2 | RED/GREEN calls (explicit) < 5s — pytest + AST acceptable |
| P3 | after-edit call (per src/ edit in REFACTOR) < 3s — pytest + quick AST |
| P4 | Fail-open: if tdd_check.py crashes, gate allows edit + logs warning |
| P5 | Stdlib only — no external dependencies (same as mvc_check.py) |
| P6 | Zero overhead when TDD mode inactive — enforcer checks tdd_mode flag first |
| P7 | Session isolation — TDD state keyed by sessionID (same as phase/skip) |

---

## 8. Integration Points with Existing Harness

| Component | Change | Risk |
|---|---|---|
| `omt_enforcer.ts` | Add 5 TDD tools + gate in `tool.execute.before` + after-edit advisory + `omt_complete` validation | Medium — enforcer is 685 LOC, adding ~150 |
| `omt_status.ts` | Add TDD state section (calls `tdd_check.py status`) | Low — additive |
| `omt_agent_guide.md` | §11/§13: add TDD rules reference | Low — documentation only |
| `test_omt_harness_e2e.py` | Add TDD contract checks | Low — additive assertions |
| `scripts/omt/` | New `tdd_check.py` | None — new file |
| `tests/scripts/omt/` | New `test_tdd_check.py` | None — new file |
| `opencode.jsonc` | No change | None — `uv *` already allowed |

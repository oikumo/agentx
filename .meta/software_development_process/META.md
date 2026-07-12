# software_development_process — OMT++ SDLC (grep-friendly)

> **Purpose**: Structured SDLC phases following OMT++ methodology — every task moves through Analysis → Design → Programming → Testing with visible artifacts.
> **Reference**: `omt_agent_guide.md` — complete methodology (read before any task).

---

# SECTION:PHASES — Phase Directory Map (grep:PHASE_)
| Phase | Dir | Purpose | Key Output |
|-------|-----|---------|------------|
| 1 | `1.project/` | Project scoping & feasibility | Go/no-go, effort estimate, preliminary design |
| 2 | `2.requirements/` | WHAT users need | Use cases, operation lists, analysis class diagrams |
| 3 | `3.analysis/` | Domain concepts & UI specs | Analysis class diagrams, data dictionary, UI spec |
| 4 | `4.design/` | HOW to implement | Component diagrams, design class diagrams, sequence diagrams |
| 5 | `5.implementation/` | Source code (MVC++) | Source code, unit tests |
| 6 | `6.testing/` | Verify & validate | Test reports, defect logs, verified system |
| 7 | `7.integration/` | Full workflow validation | Integration test reports |

---

# SECTION:STRUCTURE — Subdirectory Structure (grep:STRUCTURE_)
```
software_development_process/
├── META.md                          # This file
├── omt_agent_guide.md               # Complete OMT++ methodology for agents
├── 1.project/
│   ├── META.md
│   └── PROJECT_SUMMARY.md           # agentx project summary
├── 2.requirements/
│   ├── META.md
│   ├── documentation/
│   │   └── META.md
│   └── features/
│       ├── META.md
│       └── feature_XXX.<slug>/
│           ├── FEATURE.md
│           └── plan/PLAN.md
├── 3.analysis/
│   └── META.md
│   └── features/feature_XXX.<slug>/
│       └── analysis_*.md
├── 4.design/
│   ├── META.md
│   ├── behavior/BEHAVIOR.md
│   ├── structure/STRUCTURE.md
│   └── features/feature_XXX.<slug>/
│       ├── design_*.md
│       └── operation_spec_*.md
├── 5.implementation/
│   ├── META.md
│   └── features/feature_XXX.<slug>/
│       └── impl_notes.md
├── 6.testing/
│   ├── META.md
│   └── features/feature_XXX.<slug>/
│       └── test_report.md
└── 7.integration/
    └── META.md
```

---

# SECTION:ARTIFACTS — Phase Artifact Requirements (grep:ARTIFACT_)
Per `omt_agent_guide.md` §12 / `META_HARNESS.md` RULE_RIGOR:

| Task Type | Analysis | Design | Programming | Testing |
|-----------|----------|--------|-------------|---------|
| `bug_fix` | — | — | phase only | phase only |
| `minor_feature` | — | quick op list | phase only | phase only |
| `major_feature` | use case + analysis | **design doc required** | phase + TDD | phase + system tests |
| `new_screen` | use case + dialog | **design doc required** | phase + TDD | phase + system tests |
| `refactor` | — | — | phase only | phase only |
| `test` | — | — | — | phase only |
| `docs` | — | — | — | — |

> **Major/New Screen**: `design_*.md` must exist on disk before `src/` edits allowed.
> Scaffold: `uv run scripts/omt/new_feature.py "<name>" --type major_feature|new_screen`

---

# SECTION:FEATURES — Feature Directory Pattern (grep:FEATURE_)
Each feature gets a slug: `feature_NNN.short_name` (short) or `feature_NNN.full_description` (scaffolded).
Artifacts organized by phase under phase directories:
- `2.requirements/features/feature_XXX/FEATURE.md` + `plan/PLAN.md`
- `3.analysis/features/feature_XXX/analysis_*.md`
- `4.design/features/feature_XXX/design_*.md` + `operation_spec_*.md`
- `5.implementation/features/feature_XXX/impl_notes.md`
- `6.testing/features/feature_XXX/test_report.md`

---

# SECTION:XREF — Cross-References (grep:XREF_)
XREF_HARNESS: `.meta/META_HARNESS.md` — SECTION:RULES, SECTION:TDD, SECTION:RIGOR, SECTION:TREE
XREF_GUIDE: `omt_agent_guide.md` — §2(Phase), §12(Artifacts), §13(Checklist)
XREF_DOC: `.meta/doc/` — current-state summary (architecture, features, subsystems, data_flow, persistence, extending)
XREF_ROOT: `WORK.md` (task tracking), `AGENTS.md` (agent rules)
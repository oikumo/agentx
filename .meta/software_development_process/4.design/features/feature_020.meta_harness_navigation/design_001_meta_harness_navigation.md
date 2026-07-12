# Design: feature_020.meta_harness_navigation

> **Feature:** Meta Harness Navigation System
> **Type:** major_feature
> **Phase:** Design (pending Analysis completion)
> **Status:** Scaffolded — fill in during Design phase

---

## 1. Overview

**Problem:** The META HARNESS documentation ecosystem (META_HARNESS.md, AGENTS.md, omt_agent_guide.md, doc/omt++/*, .meta/META.md, software_development_process/META.md) is comprehensive but not optimized for LLM agent navigation via `grep`/`glob` tools. Agents must read entire files to find relevant sections.

**Solution:** Restructure all META HARNESS related files with:
- Machine-readable `SECTION:` headers with `grep:` tags
- Consistent cross-reference system (`XREF_`)
- Quick-reference workflow patterns (`QUICK_`)
- Tool/command catalog (`CMD_`)
- Error/warning codes (`ERR_`, `WRN_`)
- Task type and phase enums (`TT_`, `PHASE_`)

---

## 2. Requirements (from Analysis)

| Requirement | Source |
|-------------|--------|
| All .md files grep-navigable with standard patterns | Analysis |
| Consistent SECTION: header format across all files | Analysis |
| Cross-reference map between all META HARNESS docs | Analysis |
| Quick workflow patterns for common agent queries | Analysis |
| Integration with opencode plugin tools (omt_phase, omt_status, etc.) | Analysis |
| Zero information loss from original content | Analysis |

---

## 3. Architecture

### 3.1 File Structure (Updated)

```
.meta/
├── META.md                              # Index with SECTION:STRUCTURE, SECTION:KEY_DOCS, SECTION:WORKFLOW
├── META_HARNESS.md                      # SECTION:RULES, SECTION:TDD, SECTION:ERRORS, SECTION:CMDS, SECTION:QUICK, SECTION:XREF
├── software_development_process/
│   ├── META.md                          # SECTION:PHASES, SECTION:ARTIFACTS, SECTION:FEATURES
│   └── omt_agent_guide.md               # SECTION:META, SECTION:SCOPE + compressed methodology
├── doc/omt++/
│   ├── README.md                        # SECTION:INVENTORY, SECTION:MAINT, SECTION:RELATED, SECTION:ORIENT
│   ├── architecture.md                  # SECTION:MVCPP, SECTION:PARTNER, SECTION:FAST, SECTION:PROVIDER, SECTION:COMMAND, SECTION:DP, SECTION:STACK, SECTION:CONFIG, SECTION:DECISIONS
│   ├── data_flow.md                     # SECTION:BOOT, SECTION:NAV, SECTION:AGENT_CYCLE, SECTION:DEMO, SECTION:CHAT, SECTION:RAG_INGEST, SECTION:RAG_QUERY, SECTION:SESSION, SECTION:PERSISTENCE_FLOW
│   ├── subsystems.md                    # SECTION:AGENT, SECTION:RAG, SECTION:SESSION, SECTION:AI, SECTION:UI, SECTION:DEMO, SECTION:UTILS
│   ├── persistence.md                   # SECTION:CONVENTION, SECTION:DATABASES, SECTION:AGENT_SCHEMA, SECTION:SESSION_SCHEMA, SECTION:RAG_SCHEMA, SECTION:FILESYSTEM, SECTION:DP_CLASSES
│   ├── features.md                      # SECTION:CATALOG, SECTION:F001..F011, SECTION:CROSSCUT
│   └── extending.md                     # SECTION:BEFORE, SECTION:CMD, SECTION:SCREEN, SECTION:TOOL, SECTION:CHECKLIST, SECTION:QUICKREF
```

### 3.2 Grep Patterns Standard

All files use prefix convention:
| Prefix | Purpose | Example |
|--------|---------|---------|
| `SECTION:` | Major section header | `SECTION:RULES — Core Enforcement Rules (grep:RULE_)` |
| `RULE_` | Enforcement rule | `RULE_R1: src/edit REQUIRES omt_phase` |
| `ERR_` | Hard block | `ERR_V2M: View imports Model` |
| `WRN_` | Soft warning | `WRN_SQL_DP: SQL outside DP classes` |
| `CMD_` | Tool signature | `CMD_OMT_PHASE: omt_phase{task_type,phase,scope}` |
| `QUICK_` | Common workflow | `QUICK_START_MAJOR: omt_phase → new_feature.py → design → TDD` |
| `XREF_` | Cross-reference | `XREF_GUIDE: omt_agent_guide.md §2,§11.4,§12` |
| `TT_` | Task type enum | `TT_MAJOR_FEATURE: major_feature` |
| `PHASE_` | Phase enum | `PHASE_PROGRAMMING: Programming` |
| `FEAT_` | Feature detail | `FEAT_007_GOAL: Complete intelligent-agent subsystem` |

---

## 4. Component Design

### 4.1 META_HARNESS.md (Primary Quick Reference)
**Already complete** — restructured with 14 SECTION: blocks, 751 words, grep-optimized.

### 4.2 AGENTS.md (System Rules)
**Already complete** — compressed to 45 lines, references META_HARNESS.md for detail.

### 4.3 omt_agent_guide.md (Methodology)
**Already complete** — 718 lines, all 16 sections preserved with compressed formatting.

### 4.4 doc/omt++/* (Technical Documentation)
**Already complete** — all 6 files have SECTION: headers, grep tags, cross-refs.

### 4.5 .meta/META.md + software_development_process/META.md
**Already complete** — directory indexes with SECTION:STRUCTURE, SECTION:PHASES, SECTION:KEY_DOCS.

---

## 5. Integration Points

| Component | Integration |
|-----------|-------------|
| `omt_enforcer.ts` | Reads phase from ledger; references META_HARNESS.md RULE_* codes in block messages |
| `omt_status.ts` | Returns structured metadata; references SECTION: keys |
| `omt_phase` tool | Validates `task_type` against `TT_*`; `phase` against `PHASE_*` |
| `new_feature.py` | Scaffolds feature dirs; creates `design_001_*.md` with SECTION: template |
| `mvc_check.py` | Error codes match `ERR_*`/`WRN_*` in META_HARNESS.md |

---

## 6. Operations Specifications

| Operation | Spec |
|-----------|------|
| **Agent startup** | Read WORK.md → AGENTS.md → META_HARNESS.md → omt_agent_guide.md |
| **Before src/ edit** | `grep "CMD_OMT_PHASE" .meta/META_HARNESS.md` → `omt_phase{...}` |
| **Find blocked edits** | `grep "ERR_" .meta/META_HARNESS.md` |
| **TDD workflow** | `grep "QUICK_TDD_" .meta/META_HARNESS.md` |
| **Cross-ref lookup** | `grep "XREF_" .meta/META_HARNESS.md` |
| **Status check** | `omt_status` → returns structured + formatted output |

---

## 7. Test Plan

| Test | Method |
|------|--------|
| Grep finds all SECTION: headers | `grep -r "SECTION:" .meta/ .meta/doc/omt++/` |
| All RULE_ codes referenced in enforcer | `grep "RULE_" .meta/META_HARNESS.md` vs `grep "RULE_" .opencode/plugin/omt_enforcer.ts` |
| All ERR_ codes match mvc_check.py | `grep "ERR_" .meta/META_HARNESS.md` vs `grep "ERROR" scripts/omt/mvc_check.py` |
| All CMD_ tools exist as omt_* | `grep "CMD_" .meta/META_HARNESS.md` → check tool registry |
| QUICK_ workflows executable | Manual verification of each QUICK_ pattern |
| Zero info loss | Diff compressed vs original for each file (semantic equivalence) |

---

## 8. Deliverables

| Artifact | Location | Status |
|----------|----------|--------|
| META_HARNESS.md (restructured) | `.meta/META_HARNESS.md` | ✅ Done |
| AGENTS.md (compressed) | `AGENTS.md` | ✅ Done |
| omt_agent_guide.md (compressed) | `.meta/software_development_process/omt_agent_guide.md` | ✅ Done |
| doc/omt++/* (6 files, compressed + grep tags) | `.meta/doc/omt++/*.md` | ✅ Done |
| .meta/META.md (index) | `.meta/META.md` | ✅ Done |
| software_development_process/META.md | `.meta/software_development_process/META.md` | ✅ Done |
| **This design doc** | `4.design/features/feature_020.../design_001_meta_harness_navigation.md` | ✅ Scaffolded |

---

## 9. Next Steps (Design → Programming)

1. **Complete Analysis** — Verify all requirements captured
2. **omt_complete** — Advance to Design phase: `omt_complete{feature:"feature_020.meta_harness_navigation", advance_to:"Design"}`
3. **omt_phase** — Enter Programming: `omt_phase{task_type:"major_feature", phase:"Programming", scope:"Implement navigation tool", feature:"feature_020.meta_harness_navigation"}`
4. **Implement** — Create opencode plugin tool `omt_nav` for structured navigation
5. **TDD** — Auto-activated (major_feature in Programming)
6. **Testing** — Verify grep patterns work, tool functions
7. **omt_complete** — Advance to Testing → Done
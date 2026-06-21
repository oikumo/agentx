# .meta 

> **Purpose**: Central repository for all development metadata, documentation, and process artifacts following the OMT++ methodology. This directory contains everything needed to understand, maintain, and evolve the agentx project.

---

## Directory Structure

```
.meta/
├── META.md                              # This file - overview of .meta directory
├── software_development_process/        # OMT++ SDLC artifacts organized by phase
│   ├── META.md                          # Process overview
│   ├── omt_agent_guide.md               # Complete OMT++ methodology guide for agents
│   ├── 1.project/                       # Project scoping & feasibility studies
│   │   ├── META.md
│   │   └── PROJECT_SUMMARY.md           # agentx project summary
│   ├── 2.requirements/                  # Use cases, operation lists, analysis classes
│   │   ├── META.md
│   │   ├── documentation/               # Requirements documentation
│   │   └── features/                    # Feature-specific requirements
│   ├── 3.analysis/                      # Domain concepts, analysis class diagrams
│   │   └── META.md
│   ├── 4.design/                        # Architecture, component diagrams, interfaces
│   │   └── META.md
│   ├── 5.implementation/                # Source code guidelines, MVC++ patterns
│   │   └── META.md
│   ├── 6.testing/                       # Unit, integration, system test strategies
│   │   └── META.md
│   └── 7.integration/                   # Full workflow validation
│       └── META.md
├── proof_of_concepts/                   # Technical feasibility validation
│   └── META.md
└── prototypes/                          # UI mockups & interaction flow validation
    └── META.md
```

---

## Directory Descriptions

### software_development_process/
The complete OMT++ methodology implementation for agentx. Every feature, bug fix, and enhancement moves through these phases with visible artifacts:

1. **Project** - Feasibility studies answering "should we do this?" before any work begins
2. **Requirements** - WHAT users need (use cases, operations, analysis models)
3. **Analysis** - Domain concepts and UI behavior specifications
4. **Design** - HOW we implement it (architecture, components, interfaces)
5. **Implementation** - Source code following MVC++ and Abstract Partner patterns
6. **Testing** - Three-stage testing strategy (unit → integration → system)
7. **Integration** - End-to-end workflow validation against use cases

**Key Document**: `omt_agent_guide.md` - The complete OMT++ methodology condensed for AI coding agents. **Must be read before any coding task.**

### proof_of_concepts/
Validates technical feasibility and architecture decisions before full implementation. Used for:
- Testing new LLM provider integrations
- Validating database schema changes
- Proving architectural patterns work
- Risk reduction for high-complexity features

### prototypes/
Rapid UI mockups and interaction flows to validate use cases and dialog designs. Used for:
- Testing new screen layouts
- Validating command interaction patterns
- User experience experiments
- Abstract Partner interface designs

---

## How to Use This Directory

### For New Features
1. Start in `software_development_process/1.project/` - assess feasibility
2. Move to `2.requirements/` - define use cases and operations
3. Proceed through Analysis → Design → Implementation → Testing
4. Create artifacts in each phase directory before coding

### For Bug Fixes
1. Identify the affected component in `5.implementation/`
2. Check `6.testing/` for existing test coverage
3. Follow OMT++ process: Analysis (root cause) → Design (fix approach) → Implementation → Testing

### For Learning the Codebase
1. Read `software_development_process/omt_agent_guide.md` first
2. Review `1.project/PROJECT_SUMMARY.md` for high-level overview
3. Explore phase directories to understand the development workflow

---

## OMT++ Methodology Quick Reference

**Four Phases** (never skip):
- **Analysis** → WHAT is the problem?
- **Design** → HOW will we solve it?
- **Programming** → Write the code
- **Testing** → Does it work?

**Two Parallel Paths** (model both):
- **Static** → Classes, components, file structure
- **Functional** → Use cases, sequences, interactions

**Core Architecture**:
- **MVC++** → Model-View-Controller with strict layer separation
- **Abstract Partner** → Interface-based View↔Controller communication
- **Command Pattern** → Top-level input dispatch
- **Database Partner (DP)** → All SQL encapsulated in DP classes

---

## Related Files

- **WORK.md** (root) - Active development task tracking
- **AGENTS.md** (root) - Agent behavior rules and process enforcement
- **README.md** (root) - User-facing project documentation



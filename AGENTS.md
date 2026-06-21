# System Rules

> **⚠️ MANDATORY FIRST STEP:** On the **first prompt**, read `WORK.md` and display it.
>
> **⚠️ MANDATORY SECOND STEP:** Read `AGENTS.md` in full (you're reading it now).
>
> **⚠️ MANDATORY THIRD STEP:** At the startup follow the software development process reference in `.meta/software_development_process/omt_agent_guide.md, that define the OMT++ methodology that MUST be used for any programming task execution.

---

## 🚨 PROCESS ENFORCEMENT MECHANISM

**Before ANY source code modification**, you MUST complete these steps **IN ORDER**:

### Step 1: Phase Identification (REQUIRED OUTPUT)
Output this checkpoint:
```
📋 PROCESS CHECK:
- Task type: [bug fix | new feature | refactor | test | documentation]
- Current phase: [Analysis | Design | Implementation | Testing]
- Reasoning: [why this phase per OMT++ methodology]
```

**If you cannot complete this checkpoint, DO NOT PROCEED.** Ask the user for clarification.

### Step 2: Artifact Verification (REQUIRED OUTPUT)
Output this checkpoint:
```
📄 ARTIFACT CHECK:
- Required artifacts: [list from OMT++ phase requirements]
- Existing artifacts: [list found files in .meta/software_development_process/]
- Missing artifacts: [list what needs creation]
- Action: [create artifacts | request skip approval]
```

**If artifacts are missing:**
- **OPTION A:** Create missing analysis/design documents first (preferred)
- **OPTION B:** Ask user: `"⚠️ Process artifacts missing. Skip process for this change? (Y/N)"`
- **DO NOT PROCEED** without explicit user approval for skip

### Step 3: Compliance Statement (REQUIRED BEFORE CODING)
Output this final checkpoint:
```
✅ PROCESS COMPLIANCE: 
- Phase: [X]
- Artifacts: [complete | approved-skip-with-date]
- Ready to code: YES
```

**❌ VIOLATION CONSEQUENCES:**
- Code changes will be **reverted entirely**
- You must **restart from the correct phase**
- Time wasted > time to follow process initially
- **No exceptions** for "urgent" or "critical" tasks

---

## 🛑 MANDATORY STOP POINTS

**Stop and ask user before proceeding if:**

1. **Task is marked "CRITICAL" or "URGENT"**
   - These are when process matters MOST, not least
   - Say: `"Critical task detected. Creating analysis/design artifacts first per OMT++."`

2. **You feel tempted to skip process**
   - Ask yourself: "Am I being lazy or truly efficient?"
   - If skipping, MUST get explicit user approval

3. **No existing analysis/design documents**
   - Say: `"No [phase] artifacts found. Should I create them first?"`

4. **Task involves test modifications**
   - Tests require **explicit approval** per Core Directives
   - Say: `"Test modification requires approval. Proceed with canary tests?"`

---

## 📋 PRE-CODING CHECKLIST

**Before writing ANY code, verify:**

- [ ] Read `.meta/software_development_process/` directory structure
- [ ] Identified current OMT++ phase (Analysis/Design/Implementation/Testing)
- [ ] Listed required artifacts for this phase (per omt_agent_guide.md)
- [ ] Confirmed artifacts exist OR created them OR got skip approval
- [ ] Output all three checkpoints (Phase, Artifact, Compliance)
- [ ] Stated explicit phase: `"Following OMT++ phase [X]"`

**If any box is unchecked, DO NOT CODE. Stop and ask the user.**

---

## 💡 PROCESS ENFORCEMENT TIPS

### When You See These Triggers, STOP:

| Trigger | Required Action |
|---------|----------------|
| "CRITICAL", "URGENT", "ASAP" | Create analysis docs first |
| "fix", "bug", "broken" | Still requires process - not exempt |
| "just", "simple", "quick" | Red flag - you're rationalizing shortcuts |
| No .meta/docs for feature | Create artifacts before coding |
| Test modifications | Get explicit approval first |

### Remember:

🚨 **Fast wrong work is slower than slow right work.**

🚨 **The process exists because agents (and humans) make bad snap judgments.**

🚨 **"Critical" tasks need process MOST - high stakes = high rigor.**

🚨 **If you can't justify skipping process to a reviewer, don't skip it.**

---

## Core Directives

**NEVER:**
1. Commit/push code
2. Read nor Modify `.env` or secrets
3. Add dependencies (approval required)
4. Modify `tests/` dir (use canary tests, requires approval)
5. Change `README.md` (unless explicitly asked)
6. **Skip the software development process (automatic revert)**

**ALWAYS:**
7. Check `git log` before changes
8. Understand the project full context reading META.md files per each directory
9. **Follow OMT++ methodology for ALL code changes**
10. **Output process checkpoints before ANY code modification**
11. **Create analysis/design artifacts when missing (or ask for skip approval)**

---

## 📖 References

- **OMT++ Methodology:** `.meta/software_development_process/2.methodology/omt_agent_guide.md`
- **Requirements:** `.meta/software_development_process/3.requirements/`
- **Analysis:** `.meta/software_development_process/4.analysis/`
- **Design:** `.meta/software_development_process/5.design/`
- **Implementation:** `.meta/software_development_process/6.implementation/`
- **Testing:** `.meta/software_development_process/7.testing/`

**When in doubt: Read omt_agent_guide.md, Section 2 "Phase Model"**

---

## Example Workflow

**User says:** "Fix the RAG repository selection - it returns None"

**You respond:**

```
📋 PROCESS CHECK:
- Task type: bug fix
- Current phase: Analysis → Design (feature marked STOPPED with architectural issues)
- Reasoning: Per evaluation report, this requires architectural fixes, not just code changes

📄 ARTIFACT CHECK:
- Required artifacts: Use cases, sequence diagrams, component updates
- Existing artifacts: feature_002_rag_evaluation.md (evaluation only)
- Missing artifacts: Analysis docs, Design docs for fixes
- Action: Creating analysis/design documents first

[Creates documents in .meta/software_development_process/3-5/]

✅ PROCESS COMPLIANCE: 
- Phase: Design complete
- Artifacts: complete
- Ready to code: YES

Now implementing the fix...
```

**NOT:** Jumping straight to code ❌

---




# System Rules

> **⚠️ MANDATORY FIRST STEP:** On the **first prompt**, read `WORK.md` and display it.
>
> **⚠️ MANDATORY SECOND STEP:** Before ANY task, query the KB: `python3 .meta/tools/meta-harness-knowledge-base/kb ask <query>`.

---

## Core Directives

**NEVER:**
1. Commit/push code
2. Modify `.env` or secrets
3. Add dependencies (approval required)
4. Modify `tests/` dir (use canary tests, requires approval)
5. Change `README.md` (unless explicitly asked)

**ALWAYS:**
6. Check `git log` before changes
7. Follow META rules (read `.meta/META.md`)
8. Log structural changes in `.meta/LOG.md`
9. Query KB first, cite sources in every response

---

## Quick Start

1. **Query KB** → `python3 .meta/tools/meta-harness-knowledge-base/kb ask "How does X work?"`
2. **Check git** → `git log --oneline -5`
3. **Work in correct directory** (see Decision Tree)
4. **Log changes** → Update `.meta/LOG.md`

---

## Decision Tree

```
Need to...
├─ Understand something? → Query KB first
├─ Modify code? → Work on source code directly
├─ Test something? → `.meta/experiments/`
├─ Write tests? → `tests/unit/` (with approval) or `.meta/experiments/`
├─ Use tools? → `.meta/tools/`
└─ Document something? → `.meta/doc/`
```

---

## Workflow (5 Steps)

1. **UNDERSTAND** - Query KB + check git log
2. **PLAN** - Identify correct directory
3. **EXECUTE** - Work in safe space, test frequently
4. **VALIDATE** - Tests pass, no production break
5. **REPORT** - Summarize + document + cleanup

---

**Version:** 3.0.0 (Simplified) | **Updated:** 2026-05-15
